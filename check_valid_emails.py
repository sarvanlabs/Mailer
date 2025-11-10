import os
from pathlib import Path
import pymysql, pandas as pd
from dotenv import load_dotenv
import json, time, hmac, hashlib, base64, secrets
import utils
import re


EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
BLOCKLIST = ("info@", "no-reply@", "support@", "test@", "admin@", "hr@", "career@")


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

def is_clean_email(e):
    e = e.lower()
    return EMAIL_REGEX.match(e) and not e.startswith(BLOCKLIST)


def fetch_emails(start_date, end_date, engine=None):
    """
    Pull companies with incorporation date in [start_date, end_date).
    """
    try:
        condition = f"""cmn.Class_of_Company = 'Private' 
        and cmn.Whether_Listed_or_not = 'Unlisted'
        and cmn.Paid_up_Capital_Rs < 2000000
        and cmn.is_unsubscribed = 0
        and cmn.Date_of_Incorporation >= '{start_date}' AND cmn.Date_of_Incorporation < '{end_date}'
        and cmn.Company_Name not like '%technology%';"""
        DB_QUERY_FETCH_EMAILS = f"""SELECT cmn.Company_Name, 
        cmn.Email_Id, 
        cmn.is_unsubscribed
        from company_master_new cmn where {condition}"""
        print("DB_QUERY_FETCH_EMAILS ::: ",DB_QUERY_FETCH_EMAILS)
        return pd.read_sql(DB_QUERY_FETCH_EMAILS, con=engine)
    except Exception as e:
        print(f"Error fetching emails: {e}")

def main():
    conn = return_connection()
    try:
        emails = fetch_emails("2023-01-20", "2023-01-30",conn)
        print(f"Fetched {emails} emails.")
        # sm = utils.SecretCache(region="us-east-1")
        # HMAC_SECRET = sm.get("HMAC_SECRET")
        # print(f"HMAC Secret fetched.", HMAC_SECRET)
        # for email in emails["Email_id"]:
        #     token = make_token(
        #         email, HMAC_SECRET.get("hmac"),
        #         email_type="bulk_campaign",
        #         campaign_month="oct_2025",
        #     )
        #     link = f"https://unsubscribe.sarvanlabs.com/unsubscribe?e={token}"
        #     emails["unsubscribe_link"] = link
        invalid_count = 0
        for e in emails["Email_Id"].to_list():
            if not is_clean_email(e):
                invalid_count += 1
                print(f"Invalid email detected: {e}")

        print(f"Total invalid emails: {invalid_count} out of {len(emails)}")
        # print(emails["unsubscribe_link"])
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
    import resource; print(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024)