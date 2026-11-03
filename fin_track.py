import sqlite3
import random
import hashlib
from datetime import datetime

# Database Connection
conn = sqlite3.connect("fintrack.db")
cursor = conn.cursor()


# Create Database Tables
def create_tables():

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS accounts (
        account_no INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        pin TEXT NOT NULL,
        balance REAL DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_no INTEGER,
        transaction_type TEXT,
        amount REAL,
        date TEXT
    )
    """)

    conn.commit()


# Hash PIN
def hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()


# Create Account
def create_account():

    print("\n===== CREATE NEW ACCOUNT =====")

    name = input("Enter Account Holder Name: ")
    pin = input("Set 4-digit PIN: ")

    if not name.strip():
        print("Name cannot be empty!")
        return

    if len(pin) != 4 or not pin.isdigit():
        print("PIN must contain exactly 4 digits!")
        return

    account_no = random.randint(100000, 999999)

    cursor.execute("""
    INSERT INTO accounts
    VALUES (?, ?, ?, ?)
    """, (account_no, name, hash_pin(pin), 0.0))

    conn.commit()

    print("\nAccount Created Successfully!")
    print("Your Account Number:", account_no)


# Login
def login():

    print("\n===== CUSTOMER LOGIN =====")

    try:
        account_no = int(input("Enter Account Number: "))
        pin = input("Enter PIN: ")
    except ValueError:
        print("Invalid input!")
        return None

    cursor.execute("""
    SELECT * FROM accounts
    WHERE account_no = ? AND pin = ?
    """, (account_no, hash_pin(pin)))

    account = cursor.fetchone()

    if account:
        print("\nLogin Successful!")
        print("Welcome", account[1])
        return account_no

    print("Invalid Account Number or PIN!")
    return None


# Check Balance
def check_balance(account_no):

    cursor.execute("""
    SELECT balance FROM accounts
    WHERE account_no = ?
    """, (account_no,))

    result = cursor.fetchone()

    if result:
        print("\nAvailable Balance: ₹", format(result[0], ".2f"))


# Record Transaction
def record_transaction(account_no, transaction_type, amount):

    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO transactions
    (account_no, transaction_type, amount, date)
    VALUES (?, ?, ?, ?)
    """, (account_no, transaction_type, amount, date))


# Deposit Money
def deposit(account_no):

    try:
        amount = float(input("Enter Deposit Amount: ₹"))

        if amount <= 0:
            print("Enter a valid positive amount!")
            return

        cursor.execute("""
        UPDATE accounts
        SET balance = balance + ?
        WHERE account_no = ?
        """, (amount, account_no))

        record_transaction(account_no, "Deposit", amount)

        conn.commit()

        print("\nDeposit Successful!")
        check_balance(account_no)

    except ValueError:
        print("Invalid amount!")


# Withdraw Money
def withdraw(account_no):

    try:
        amount = float(input("Enter Withdrawal Amount: ₹"))

        if amount <= 0:
            print("Enter a valid positive amount!")
            return

        cursor.execute("""
        SELECT balance FROM accounts
        WHERE account_no = ?
        """, (account_no,))

        balance = cursor.fetchone()[0]

        if amount > balance:
            print("Insufficient Balance!")
            return

        cursor.execute("""
        UPDATE accounts
        SET balance = balance - ?
        WHERE account_no = ?
        """, (amount, account_no))

        record_transaction(account_no, "Withdrawal", amount)

        conn.commit()

        print("\nWithdrawal Successful!")
        check_balance(account_no)

    except ValueError:
        print("Invalid amount!")


# Transfer Money
def transfer_money(account_no):

    try:
        receiver = int(input("Enter Receiver Account Number: "))
        amount = float(input("Enter Transfer Amount: ₹"))

        if receiver == account_no:
            print("Cannot transfer money to the same account!")
            return

        if amount <= 0:
            print("Enter a valid positive amount!")
            return

        cursor.execute("""
        SELECT balance FROM accounts
        WHERE account_no = ?
        """, (account_no,))

        sender = cursor.fetchone()

        cursor.execute("""
        SELECT account_no FROM accounts
        WHERE account_no = ?
        """, (receiver,))

        receiver_exists = cursor.fetchone()

        if sender is None or receiver_exists is None:
            print("Invalid account number!")
            return

        if sender[0] < amount:
            print("Insufficient Balance!")
            return

        try:
            cursor.execute("""
            UPDATE accounts
            SET balance = balance - ?
            WHERE account_no = ?
            """, (amount, account_no))

            cursor.execute("""
            UPDATE accounts
            SET balance = balance + ?
            WHERE account_no = ?
            """, (amount, receiver))

            record_transaction(
                account_no, "Transfer Sent", amount
            )

            record_transaction(
                receiver, "Transfer Received", amount
            )

            conn.commit()

            print("\nTransfer Successful!")

        except Exception:
            conn.rollback()
            raise

    except ValueError:
        print("Invalid input!")


# Transaction History
def transaction_history(account_no):

    cursor.execute("""
    SELECT transaction_type, amount, date
    FROM transactions
    WHERE account_no = ?
    ORDER BY id DESC
    """, (account_no,))

    records = cursor.fetchall()

    print("\n===== TRANSACTION HISTORY =====")

    if not records:
        print("No transactions found.")
        return

    for record in records:

        print("----------------------------")
        print("Type:", record[0])
        print("Amount: ₹", record[1])
        print("Date:", record[2])


# Customer Dashboard
def customer_menu(account_no):

    while True:

        print("\n========== FIN TRACK ==========")
        print("1. Check Balance")
        print("2. Deposit Money")
        print("3. Withdraw Money")
        print("4. Transfer Money")
        print("5. Transaction History")
        print("6. Logout")

        choice = input("Enter Your Choice: ")

        if choice == "1":
            check_balance(account_no)

        elif choice == "2":
            deposit(account_no)

        elif choice == "3":
            withdraw(account_no)

        elif choice == "4":
            transfer_money(account_no)

        elif choice == "5":
            transaction_history(account_no)

        elif choice == "6":
            print("Logged Out Successfully!")
            break

        else:
            print("Invalid Choice! Try Again.")


# Main Function
def main():

    create_tables()

    while True:

        print("\n================================")
        print("       FIN TRACK BANKING")
        print("================================")

        print("1. Create Account")
        print("2. Login")
        print("3. Exit")

        choice = input("Enter Your Choice: ")

        if choice == "1":
            create_account()

        elif choice == "2":

            account_no = login()

            if account_no:
                customer_menu(account_no)

        elif choice == "3":

            print("\nThank You For Using FIN TRACK!")
            conn.close()
            break

        else:
            print("Invalid Choice! Try Again.")


# Program Execution
if __name__ == "__main__":
    main()