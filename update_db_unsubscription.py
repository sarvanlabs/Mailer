import boto3
import json
import utils
from botocore.exceptions import ClientError

BUCKET = "sarvanlabs-unsubs-us-east-1"
PREFIX = "unsubs/"

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
    # QUERY = f"SELECT * FROM company_master_new WHERE Email_Id in ({emails});"
    arr = []
    for d in data:
        arr.append(d['email'])
    print(json.stringify(arr))


if __name__ == "__main__":
    main()