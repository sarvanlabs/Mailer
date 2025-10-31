import os
from pathlib import Path
import pymysql, pandas as pd
from dotenv import load_dotenv
import json, time, hmac, hashlib, base64, secrets
import utils


def return_connection():
    sm = utils.SecretCache(region="us-east-1")
    db_creds = sm.get("MySQL_local")
    DB_HOST = db_creds.get("host")
    DB_USER = db_creds.get("user")
    DB_PASSWORD = db_creds.get("password")
    DB_DATABASE_NAME = db_creds.get("database")
    print("Establishing database connection...")
    print(f"DB Host: {DB_HOST}, DB User: {DB_USER}, DB Name: {DB_DATABASE_NAME}")
    connection = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_DATABASE_NAME
    )
    return connection


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")

def make_token(
    email: str,
    secret: str,
    email_type: str | None = None,
    campaign_month: str | None = None,
) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    now = int(time.time())
    payload = {
        "e": email.lower(),
        "iat": now,
        "nbf": now,
        #"exp": now + 1 * 60,
        "nonce": secrets.token_urlsafe(12),
    }
    if email_type: payload["email_type"] = email_type
    if campaign_month:   payload["campaign_month"] = campaign_month

    head = b64url(json.dumps(header, separators=(",", ":"), ensure_ascii=True).encode())
    body = b64url(json.dumps(payload, separators=(",", ":"), ensure_ascii=True).encode())

    signing_input = f"{head}.{body}".encode()
    sig = hmac.new(secret.encode(), signing_input, hashlib.sha256).digest()
    token = f"{head}.{body}.{b64url(sig)}"
    return token


def fetch_emails(conn=None):
    query = "SELECT Email_id FROM company_master_new LIMIT 10";
    emails = pd.read_sql(query, con=conn)
    return emails

def main():
    conn = return_connection()
    try:
        emails = fetch_emails(conn)
        print(f"Fetched {emails} emails.")
        sm = utils.SecretCache(region="us-east-1")
        HMAC_SECRET = sm.get("HMAC_SECRET")
        print(f"HMAC Secret fetched.", HMAC_SECRET)
        for email in emails["Email_id"]:
            token = make_token(
                email, HMAC_SECRET.get("hmac"),
                email_type="bulk_campaign",
                campaign_month="oct_2025",
            )
            link = f"https://unsubscribe.sarvanlabs.com/unsubscribe?e={token}"
            emails["unsubscribe_link"] = link
        print(emails["Email_id"])
        print(emails["unsubscribe_link"])
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
    import resource; print(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024)