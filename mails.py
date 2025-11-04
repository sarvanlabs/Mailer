def email_exists(records: list[dict], email: str) -> bool:
    target = email.strip().lower()
    return any((r.get("email") or "").strip().lower() == target for r in records)



if __name__ == "__main__":
    records = [{"email":"abc@abc.in"}, {"email":"xyz.m@xyz.com"}]
    if not email_exists(records, "xyzy.m@xyz.com"):
        print("Email not found")
