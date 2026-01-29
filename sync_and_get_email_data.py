import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

SOURCE_DB_URL = os.getenv("REMOTE_BLUEOCEAN_DB_URL")   # BlueOcean
TARGET_DB_URL = os.getenv("LOCAL_DB_URL")   # Local

SOURCE_TABLE = "company_master_new"
TARGET_TABLE = "company_master_new"
BATCH_SIZE   = 10000

source_engine = create_engine(SOURCE_DB_URL, pool_pre_ping=True)
target_engine = create_engine(TARGET_DB_URL, pool_pre_ping=True)


# ---------------------------
# Fetch from Source
# ---------------------------

def fetch_rows(date_filter=None):
    sql = text(f"""
        SELECT id, CIN, Company_Name, ROC_Code, Registration_Number, 
               Company_Category, Company_SubCategory, Class_of_Company, 
               Authorised_Capital_Rs, Paid_up_Capital_Rs, Number_of_Members, 
               Date_of_Incorporation, Registered_Address, Address_books, Email_Id, 0 as is_unsubscribed, '' as unsubscribed_at, 
               Whether_Listed_or_not, ACTIVE_compliance, Suspended_at_stock_exchange, Date_of_last_AGM, Date_of_Balance_Sheet, 
               Company_Status, auditor, inc, dnd, last_updated
                FROM {SOURCE_TABLE} where {SOURCE_TABLE}.Date_of_Incorporation > :date_filter;
    """)

    with source_engine.connect() as conn:
        return conn.execute(sql, {
            "date_filter": date_filter
        }).fetchall()


# ---------------------------
# Insert into Target
# ---------------------------

def insert_rows(rows):
    ###Insert in bulk###
    if not rows:
        return 0

    sql = text(f"""
        INSERT INTO {TARGET_TABLE}
            (id, CIN, Company_Name, ROC_Code, Registration_Number, Company_Category, Company_SubCategory, Class_of_Company, Authorised_Capital_Rs, Paid_up_Capital_Rs, Number_of_Members, Date_of_Incorporation, Registered_Address, Address_books, Email_Id, is_unsubscribed, unsubscribed_at, Whether_Listed_or_not, ACTIVE_compliance, Suspended_at_stock_exchange, Date_of_last_AGM, Date_of_Balance_Sheet, Company_Status, auditor, inc, dnd, last_updated)
        VALUES
            (:id, :CIN, :Company_Name, :ROC_Code, :Registration_Number, :Company_Category, :Company_SubCategory, :Class_of_Company, :Authorised_Capital_Rs, :Paid_up_Capital_Rs, :Number_of_Members, :Date_of_Incorporation, :Registered_Address, :Address_books, :Email_Id, :is_unsubscribed, :unsubscribed_at, :Whether_Listed_or_not, :ACTIVE_compliance, :Suspended_at_stock_exchange, :Date_of_last_AGM, :Date_of_Balance_Sheet, :Company_Status, :auditor, :inc, :dnd, :last_updated)
    """)
    payload = [
        {
            "id": r.id,
            "CIN": r.CIN,
            "Company_Name": r.Company_Name,
            "ROC_Code": r.ROC_Code,
            "Registration_Number": r.Registration_Number,
            "Company_Category": r.Company_Category,
            "Company_SubCategory": r.Company_SubCategory,
            "Class_of_Company": r.Class_of_Company,
            "Authorised_Capital_Rs": r.Authorised_Capital_Rs,
            "Paid_up_Capital_Rs": r.Paid_up_Capital_Rs,
            "Number_of_Members": r.Number_of_Members,
            "Date_of_Incorporation": r.Date_of_Incorporation,
            "Registered_Address": r.Registered_Address,
            "Address_books": r.Address_books,
            "Email_Id": r.Email_Id,
            "is_unsubscribed": r.is_unsubscribed,
            "unsubscribed_at": datetime.utcnow(),
            "Whether_Listed_or_not": r.Whether_Listed_or_not,
            "ACTIVE_compliance": r.ACTIVE_compliance,
            "Suspended_at_stock_exchange": r.Suspended_at_stock_exchange,
            "Date_of_last_AGM": r.Date_of_last_AGM,
            "Date_of_Balance_Sheet": r.Date_of_Balance_Sheet,
            "Company_Status": r.Company_Status,
            "auditor": r.auditor,
            "inc": r.inc,
            "dnd": r.dnd,
            "last_updated": r.last_updated,
        }
        for r in rows
    ]

    with target_engine.begin() as conn:
        conn.execute(sql, payload)

    return len(rows)


# ---------------------------
# Main Runner
# ---------------------------

def main():
    print("🚀 Copy started (BlueOcean → Local)")

    rows = fetch_rows(date_filter="2024-05-01")
    print(f"Fetched {len(rows)} rows from source")
    print(f"Inserting {len(rows)} rows...")
    inserted = insert_rows(rows)

    print(f"✅ Inserted {inserted} rows")

    print(f"🎯 Copy finished. Total rows inserted: {inserted}")


if __name__ == "__main__":
    main()
