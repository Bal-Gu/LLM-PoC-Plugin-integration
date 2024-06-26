import hashlib
import json
import random
import string
import time
from typing import List

import mysql.connector


class Database:
    def __init__(self, config: json):
        self.mydb = mysql.connector.connect(
            host=config["mysql_host"],
            port=config["mysql_port"],
            user=config["mysql_user"],
            password=config["mysql_password"]
        )

        self.mycursor = self.mydb.cursor()

        self.mycursor.execute("CREATE DATABASE IF NOT EXISTS Chat")

        self.mycursor.execute("USE Chat")

        # User table
        self.mycursor.execute(
            "CREATE TABLE IF NOT EXISTS user (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), admin BOOLEAN)")

        # Auth table
        self.mycursor.execute(
            "CREATE TABLE IF NOT EXISTS auth (id INT AUTO_INCREMENT PRIMARY KEY, user_id INT, password VARCHAR(255), salt VARCHAR(5), auth_token VARCHAR(255), FOREIGN KEY(user_id) REFERENCES user(id))")

        # Session table
        self.mycursor.execute(
            "CREATE TABLE IF NOT EXISTS session (id INT AUTO_INCREMENT PRIMARY KEY, user_id INT, model_name VARCHAR(255),session_name VARCHAR(255), FOREIGN KEY(user_id) REFERENCES user(id))")

        # Message table
        self.mycursor.execute(
            "CREATE TABLE IF NOT EXISTS message (id INT AUTO_INCREMENT PRIMARY KEY, user_id INT, session_id INT, order_id INT, content VARCHAR(10000), FOREIGN KEY(user_id) REFERENCES user(id), FOREIGN KEY(session_id) REFERENCES session(id),status TINYINT(1))")

        self.create_user("assistant", str(random.random()), False, 1)
        self.create_user("admin", config["admin_password"], True, 2)

    def login(self, username, password):
        # Fetch user data from the user table
        user = self.parallelize_and_fetch(False, "SELECT * FROM user WHERE username = %s", [username])
        if user:
            # Fetch authentication data from the auth table
            auth = self.parallelize_and_fetch(False, "SELECT * FROM auth WHERE user_id = %s", [user[0]])
            if auth:
                salt = auth[3]
                db_pass = auth[2]
                hash_password = hashlib.sha3_256()
                hash_password.update(str(username + password + salt).encode())
                internal_pass = hash_password.hexdigest()
                if internal_pass == db_pass:
                    return auth[4]
        return None

    def create_user(self, username, password, admin=False, user_id=-1):
        """returns True if unique"""
        user = self.parallelize_and_fetch(False, "SELECT * FROM user WHERE id = %s OR username = %s",
                                          [user_id, username])
        auth_token = ''.join(random.choices(string.ascii_letters + string.digits, k=255))
        if not user:
            salt = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
            hash_password = hashlib.sha3_256()
            hash_password.update(str(username + password + salt).encode())
            user_data = {
                "username": username,
                "admin": admin
            }
            if user_id != -1:
                user_data["id"] = user_id
            self.save("user", user_data)
            user = self.parallelize_and_fetch(False, "SELECT * FROM user WHERE username = %s", [username])
            auth_data = {
                "user_id": user[0],
                "password": hash_password.hexdigest(),
                "auth_token": auth_token,
                "salt": salt
            }
            self.save("auth", auth_data)
            return auth_token
        return None

    def save(self, table: str, data: dict):
        placeholders = ', '.join(['%s'] * len(data))
        columns = ', '.join(data.keys())
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        values = tuple(data.values())
        self.mycursor.execute(sql, values)
        self.mydb.commit()

    def update_user(self, user):
        # Generate a new token
        new_token = ''.join(random.choices(string.ascii_letters + string.digits, k=255))

        # Update the new token in the database
        self.mycursor.execute("UPDATE user SET auth_token = %s WHERE id = %s", [new_token, user[0]])
        self.mydb.commit()
        return new_token

    def parallelize_and_ignore(self, query: str, escape_values: List):
        tmp_cursor = self.mydb.cursor()
        tmp_cursor.execute("USE Chat")
        tmp_cursor.execute(query, escape_values)
        self.mydb.commit()
        tmp_cursor.close()



    def parallelize_and_index(self, query: str, escape_values: List):
        tmp_cursor = self.mydb.cursor()
        tmp_cursor.execute("USE Chat")
        tmp_cursor.execute(query, escape_values)
        self.mydb.commit()
        idx = tmp_cursor.lastrowid
        tmp_cursor.close()
        return idx


    def parallelize_and_fetch(self, fetch_multiple: bool, query: str, escape_values: List):
        tmp_cursor = self.mydb.cursor()
        tmp_cursor.execute("USE Chat")
        tmp_cursor.execute(query, escape_values)
        res = tmp_cursor.fetchall() if fetch_multiple else tmp_cursor.fetchone()

        tmp_cursor.close()
        return res
