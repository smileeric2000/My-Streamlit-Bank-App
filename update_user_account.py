
#update_user_account.py
#short python code to updates account_name and account_num for an existing user


import sqlite3

DB_PATH = "database.db"   

def get_connection():
    return sqlite3.connect(DB_PATH)


def update_user_account(old_account_num: int, new_account_num: int, new_account_name: str):
    conn = get_connection()
    cur = conn.cursor()

    #Check if old account exists
    cur.execute(
        "SELECT account_num FROM users WHERE account_num = ?",
        (old_account_num,)
    )
    if not cur.fetchone():
        conn.close()
        print("Account not found.")
        return

    #Check if new account number already exists
    cur.execute(
        "SELECT account_num FROM users WHERE account_num = ?",
        (new_account_num,)
    )
    if cur.fetchone():
        conn.close()
        print("New account number already exists.")
        return

    #Perform update
    cur.execute(
        """
        UPDATE users
        SET account_num = ?, account_name = ?
        WHERE account_num = ?
        """,
        (new_account_num, new_account_name, old_account_num)
    )

    conn.commit()
    conn.close()
    print("Account details updated successfully.")


if __name__ == "__main__":
    print("=== Update User Account ===")

    old_account = input("Enter OLD account number: ").strip()
    new_account = input("Enter NEW account number (10 digits): ").strip()
    new_name = input("Enter NEW account name: ").strip()

    #Basic validation
    if not old_account.isdigit():
        print("Old account number must be digits.")
        exit()

    if not new_account.isdigit() or len(new_account) != 10:
        print("New account number must be exactly 10 digits.")
        exit()

    if not new_name:
        print("Account name cannot be empty.")
        exit()

    update_user_account(
        old_account_num=int(old_account),
        new_account_num=int(new_account),
        new_account_name=new_name
    )
