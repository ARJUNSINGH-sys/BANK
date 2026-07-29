import os
import sys
import sqlite3

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(0, ROOT)

from database.databade import db
from Transcation.transaction import TransactionEngine


def initialize_database(db_path, schema_path):
    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        sql = open(schema_path, "r", encoding="utf-8").read()
        cursor.executescript(sql)
        conn.commit()


def prompt_credentials():
    account_no = input("Account number: ").strip()
    password = input("Password: ").strip()
    return account_no, password


def seed_sample_data(db):
    if db.fetchone_("SELECT 1 FROM customer LIMIT 1"):
        return

    if not db.fetchone_("SELECT Branch_id FROM branch_details WHERE branch_name = ?", "Main Branch"):
        db.execute_("INSERT OR IGNORE INTO nation (nation_id) VALUES (?)", "N1")
        db.execute_("INSERT OR IGNORE INTO state (state_id, nation_id) VALUES (?, ?)", "S1", "N1")
        db.execute_("INSERT OR IGNORE INTO district (DISTRICT_ID, state_id) VALUES (?, ?)", "D1", "S1")
        db.execute_("INSERT OR IGNORE INTO zonal (zonal_id, DISTRICT_ID) VALUES (?, ?)", "Z1", "D1")
        db.execute_("INSERT INTO branch_details (zonal_id, branch_name, branch_address, pin_code) VALUES (?, ?, ?, ?)",
                    "Z1", "Main Branch", "123 Main St", "100001")

    branch_id_row = db.fetchone_("SELECT Branch_id FROM branch_details WHERE branch_name = ?", "Main Branch")
    branch_id = branch_id_row[0]

    sample_customers = [
        ("password1", "Alice", "NID", "A123", "123 Cherry Ln", 1111111111, "alice@example.com", branch_id),
        ("password2", "Bob", "NID", "B234", "456 Oak Ave", 2222222222, "bob@example.com", branch_id),
        ("password3", "Charlie", "NID", "C345", "789 Pine Rd", 3333333333, "charlie@example.com", branch_id),
    ]

    for password, name, pid_type, pid, address, phone, email, branch_no in sample_customers:
        db.execute_(
            "INSERT INTO customer (password, name, personal_id_type, personal_id, address, Phone_No, Email, Branch_NO) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            password,
            name,
            pid_type,
            pid,
            address,
            phone,
            email,
            branch_no,
        )

    for customer_id, in db.fetchall_("SELECT ID_no FROM customer"):
        db.execute_("INSERT OR IGNORE INTO balance (ID_no, balance) VALUES (?, ?)", customer_id, 1000)

    db.commit_()


def main():
    db_path = os.path.join(ROOT, "branch.db")
    schema_path = os.path.join(ROOT, "database", "branch.sql")

    print("Initializing database...")
    initialize_database(db_path, schema_path)
    seed_sample_data(db)
    engine = TransactionEngine(db)

    print("Welcome to the Mini Transaction Engine")
    while True:
        print("\nMenu:")
        print("1) Login and deposit")
        print("2) Login and withdraw")
        print("3) Login and transfer")
        print("4) Check balance")
        print("5) Exit")
        choice = input("Choose an option: ").strip()

        if choice == "5":
            print("Goodbye.")
            break

        if choice == "4":
            account_no = input("Account number to check: ").strip()
            balance = engine.get_balance(account_no)
            if balance is None:
                print("Invalid account or no balance record.")
            else:
                print(f"Balance for account {account_no}: {balance}")
            continue

        account_no, password = prompt_credentials()
        if not engine.login(account_no, password):
            continue

        if choice == "1":
            amount = input("Deposit amount: ").strip()
            result = engine.deposit(amount)
            if result is not False:
                print(f"Deposit successful. New balance: {result}")
        elif choice == "2":
            amount = input("Withdraw amount: ").strip()
            result = engine.withdraw(amount)
            if result is not False:
                print(f"Withdraw successful. New balance: {result}")
        elif choice == "3":
            receiver = input("Receiver account number: ").strip()
            amount = input("Transfer amount: ").strip()
            result = engine.transfer(receiver, amount)
            if result is not False:
                print("Transfer successful.")
                print(f"Sender balance: {result['sender_balance']}")
                print(f"Receiver balance: {result['receiver_balance']}")
        else:
            print("Invalid option.")

    db.close_()


if __name__ == "__main__":
    main()
