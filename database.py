import sqlite3
from os import path
import time

DB_FILE_NAME = "database.db"

def get_user_id_by_name(username):
    db_connection = sqlite3.connect("database.db")
    cursor = db_connection.cursor()
    cursor.execute(f"""
        SELECT id FROM users WHERE username='{username}'
    """)
    user_id = cursor.fetchone()
    db_connection.commit()
    db_connection.close()
    return user_id[0]

def get_user_password(user_id):
    db_connection = sqlite3.connect("database.db")
    cursor = db_connection.cursor()
    cursor.execute(f"""
        SELECT password FROM users WHERE id='{user_id}'
    """)
    password = cursor.fetchone()
    db_connection.commit()
    db_connection.close()
    return password[0]

def user_exists(username):
    db_connection = sqlite3.connect("database.db")
    cursor = db_connection.cursor()
    cursor.execute(f"""
        SELECT id FROM users WHERE username='{username}'
    """)
    user_id = cursor.fetchone()
    db_connection.commit()
    db_connection.close()
    if user_id == None:
        return False
    else:
        return True

def create_database():
    if(path.exists("database.db")):
        return
    db_connection = sqlite3.connect("database.db")
    cursor = db_connection.cursor()
    cursor.execute("""
        CREATE TABLE users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT
        );
    """)
    db_connection.commit()

    cursor.execute("""
        CREATE TABLE messages(
            time REAL PRIMARY KEY,
            user_id INTEGER,
            content TEXT
        );
    """)
    db_connection.commit()

    db_connection.close()
    print(f"Inexistent database. Database created as '{DB_FILE_NAME}'.")

def add_user(username, password):
    db_connection = sqlite3.connect("database.db")
    cursor = db_connection.cursor()
    cursor.execute(f"""
        INSERT INTO users(username,password) VALUES ('{username}','{password}');
    """)
    db_connection.commit()
    db_connection.close()
    print(f"User '{username}' added to the database.")

def add_message(user_id, content):
    db_connection = sqlite3.connect("database.db")
    cursor = db_connection.cursor()
    t = time.time()
    cursor.execute(f"""
        INSERT INTO messages VALUES ({t}, '{user_id}','{content}');
    """)
    db_connection.commit()
    db_connection.close()

def get_user(user_id):
    db_connection = sqlite3.connect("database.db")
    cursor = db_connection.cursor()
    cursor.execute(f"""
        SELECT * FROM users WHERE id={user_id}
    """)
    user = cursor.fetchone()
    db_connection.commit()
    db_connection.close()
    return user

def printdb():
    db_connection = sqlite3.connect("database.db")
    cursor = db_connection.cursor()
    cursor.execute(f"""
        SELECT * FROM users
    """)
    users = cursor.fetchall()
    for u in users:
        print(u)
    db_connection.commit()
    db_connection.close()