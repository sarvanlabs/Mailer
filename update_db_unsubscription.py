import boto3
import json
import utils
from botocore.exceptions import ClientError
import pymysql

BUCKET = "sarvanlabs-unsubs-us-east-1"
PREFIX = "unsubs/"

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

def get_text_file(bucket: str, key: str, encoding="utf-8") -> str | None:
    try:
        s3 = boto3.client("s3", region_name="us-east-1")
        resp = s3.get_object(Bucket=bucket, Key=key)
        body_bytes = resp["Body"].read()
        text = body_bytes.decode("utf-8")         # string
        return json.loads(text)  
    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code in ("NoSuchKey", "404"):
            print("File not found:", key)
            return None
        if code == "AccessDenied":
            print("Access denied. Check IAM policy/bucket policy.")
            return None
        raise  # bubble up anything else

def main():
    OBJECT_KEY = f"{PREFIX}/unsubscribed_emails.json"
    data = get_text_file(BUCKET, OBJECT_KEY)
    arr_email = []
    arr_unsubscribed_at = []
    for d in data:
        arr_email.append(d['email'])
    in_clause = "(" + ",".join(f"'{e}'" for e in arr_email) + ")"
    # for d in data:
    #     arr_unsubscribed_at.append(d['timestamp'])
    # unsubscribed_at = "(" + ",".join(f"'{e}'" for e in arr_unsubscribed_at) + ")"
    # print("IN clause for SQL query:", in_clause)
    # QUERY = f"SELECT * FROM company_master_new WHERE Email_Id in {in_clause};"
    QUERY = f""" UPDATE company_master_new cmn
            SET cmn.is_unsubscribed=1
            WHERE cmn.Email_Id IN {in_clause};
            """
    print("SQL Query to fetch unsubscribed emails:")
    print(QUERY)
    try:
        conn = return_connection()
        with conn.cursor() as cursor:
            rows_affected = cursor.execute(QUERY)
            conn.commit()
            print(f"Query executed successfully! {rows_affected} rows were updated.")
    except pymysql.Error as e:
        print(f"Error executing query: {str(e)}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    main()