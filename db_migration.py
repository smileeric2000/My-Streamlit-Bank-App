# import sqlite3
#Python file to fix user profile issues.



# Updating database to add a column for profile picture.
# conn = sqlite3.connect("database.db")  
# cur = conn.cursor()

# cur.execute("SELECT account_num, profile_img FROM users WHERE profile_img IS NOT NULL;")

# conn.commit()
# conn.close()

# print("profile_img column added")

#A debug code to fix user profile image render

# import sqlite3

# DB_PATH = r"C:\Users\USER\data_science\bank_project/database.db"  

# ACCOUNT_NUM = 112  

# conn = sqlite3.connect(DB_PATH)
# cur = conn.cursor()

# cur.execute("""
#     SELECT account_num, LENGTH(profile_img), SUBSTR(profile_img, 1, 30)
#     FROM users
#     WHERE account_num = ?
# """, (ACCOUNT_NUM,))

# row = cur.fetchone()
# conn.close()

# if row:
#     acc, length, preview = row
#     print("Account:", acc)
#     print("Image length:", length)
#     print("Image preview:", preview)
# else:
#     print("User not found")
