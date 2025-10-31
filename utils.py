import time, json, boto3
from botocore.exceptions import ClientError

class SecretCache:
    """
    Caches AWS Secrets Manager secrets.
    Parses JSON secrets into dictionaries; non-JSON secrets are returned as {"value": secret}."""

    def __init__(self, region="us-east-1"):
        self.client = boto3.client("secretsmanager", region_name=region)
        self._cache = {}  # {secret_id: (expires_at, parsed_value)}

    def get(self, secret_id: str):
        now = time.time()
        ent = self._cache.get(secret_id)
        if ent and ent[0] > now:
            return ent[1]

        try:
            resp = self.client.get_secret_value(SecretId=secret_id)
        except ClientError as e:
            raise RuntimeError(f"Secrets Manager error for {secret_id}: {e}") from e

        val = resp.get("SecretString") or resp["SecretBinary"].decode("utf-8")
        try:
            parsed = json.loads(val)
        except json.JSONDecodeError:
            parsed = {"value": val}

        self._cache[secret_id] = (parsed)
        return parsed


if __name__ == "__main__":
    sm = SecretCache(region="us-east-1")
    secret = sm.get("MySQL_local")
    print(secret)