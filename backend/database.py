import hashlib
import json
import random
import string
import time

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
            "CREATE TABLE IF NOT EXISTS user (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), password VARCHAR(255),salt VARCHAR(5), auth_token VARCHAR(255), admin BOOLEAN)")

        # Session table
        self.mycursor.execute(
            "CREATE TABLE IF NOT EXISTS session (id INT AUTO_INCREMENT PRIMARY KEY, user_id INT, model_name VARCHAR(255), FOREIGN KEY(user_id) REFERENCES user(id))")

        # Message table
        self.mycursor.execute(
            "CREATE TABLE IF NOT EXISTS message (id INT AUTO_INCREMENT PRIMARY KEY, user_id INT, session_id INT, order_id INT, content VARCHAR(10000), FOREIGN KEY(user_id) REFERENCES user(id), FOREIGN KEY(session_id) REFERENCES session(id))")

        # Plugin table
        self.mycursor.execute(
            "CREATE TABLE IF NOT EXISTS plugin (user_id INT, internal_id INT AUTO_INCREMENT PRIMARY KEY, session_id INT, activated BOOLEAN, FOREIGN KEY(user_id) REFERENCES user(id), FOREIGN KEY(session_id) REFERENCES session(id))")

        self.create_user("assitent",str(random.random()),False,1)
        self.create_user("admin", config["admin_password"], True, 2)

    def login(self,username,password):
        self.mycursor.execute("SELECT * FROM user WHERE username = %s",[username])
        user = self.mycursor.fetchone()
        if user :
            salt = user[3]
            db_pass = user[2]
            hash_password = hashlib.sha3_256()
            hash_password.update(str(username + password + salt).encode())
            internal_pass = hash_password.hexdigest()
            if internal_pass == db_pass:
                return user.get("auth_token")
        return None
    def create_user(self,username,password,admin=False,user_id=-1):
        """returns True if unique"""
        self.mycursor.execute("SELECT * FROM user WHERE id = %s",[user_id])
        user = self.mycursor.fetchone()
        if not user:
            salt = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
            hash_password = hashlib.sha3_256()
            hash_password.update(str(username + password + salt).encode())
            data = {
                "username": username,
                "password": hash_password.hexdigest(),
                "auth_token": ''.join(random.choices(string.ascii_letters + string.digits, k=255)) ,
                "admin": admin,
                "salt": salt
            }
            if id != -1:
                data["id"] = user_id
            self.save("user", data)
            return True
        return False

    def save(self, table: str, data: dict):
        placeholders = ', '.join(['%s'] * len(data))
        columns = ', '.join(data.keys())
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        values = tuple(data.values())
        self.mycursor.execute(sql, values)
        self.mydb.commit()

    def update_user(self,user):
        # Generate a new token
        new_token = ''.join(random.choices(string.ascii_letters + string.digits, k=255))

        # Update the new token in the database
        self.mycursor.execute("UPDATE user SET auth_token = %s WHERE id = %s", [new_token, user[0]])
        self.mydb.commit()
        return new_token

