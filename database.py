# this is SQLite3 database stuff
# not commented properly yet

import string
import random
import sqlite3
import hashlib

#creates users and profiles table
def init():
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users
    (rowid INTEGER PRIMARY KEY, username TEXT, password TEXT, salt TEXT)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS profiles
    (rowid INTEGER PRIMARY KEY, userid INTEGER, fname TEXT, lname TEXT, avatar TEXT)""")

    cursor.close()
    connection.close()
    return

#attempts to register a user
def user_register(username, password):
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()
    salt = ''.join(random.choices(string.printable, k=10))

    #check if username already exists
    data = (username,)
    alreadyexists = cursor.execute("SELECT username FROM users WHERE username = (?)", data).fetchall()
    if alreadyexists == []: #username is unique
        #store new account in users
        hash = hashlib.sha256()
        hash.update(password.encode()+salt.encode())
        passwordHash = hash.hexdigest()
        data = (username,passwordHash,salt)
        cursor.execute("INSERT INTO users (username, password, salt) VALUES(?,?,?)", data)
        connection.commit()
        #store new profile in profiles
        userid = cursor.execute("SELECT rowid FROM users WHERE username = (?)", (username,)).fetchall()[0][0]
        data = (userid,"John","Doe","/static/avatars/cursed_donut.png")
        cursor.execute("INSERT INTO profiles (userid, fname, lname, avatar) VALUES(?,?,?,?)", data)
        connection.commit()
        print(username + " registered")
        cursor.close()
        connection.close()
        return True     
    
    cursor.close()
    connection.close()
    return False

#attempts to login a user
def user_login(username, password):
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()
    #check if username exists
    if cursor.execute("SELECT username FROM users WHERE username = (?)", (username,)).fetchall() != []:
        salt = cursor.execute("SELECT salt FROM users WHERE username = (?)", (username,)).fetchall()
        hash = hashlib.sha256()
        hash.update(password.encode()+salt[0][0].encode())
        passwordHash = hash.hexdigest()
        actualpswd = cursor.execute("SELECT password FROM users WHERE username = (?)", (username,)).fetchall()[0][0]
        #check if password is correct
        if passwordHash == actualpswd:
            print(username+" logged in")
            cursor.close()
            connection.close()
            return True
        
    print("invalid username or password")
    cursor.close()
    connection.close()
    return False

#deletes an account
def delete_account(username):
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    rowid = cursor.execute("SELECT rowid FROM users where username = (?)", (username,)).fetchall()[0][0]
    cursor.execute("DELETE from users WHERE username = (?)", (username,))
    connection.commit()
    cursor.execute("DELETE from profiles WHERE userid = (?)", (rowid,))
    connection.commit()
    print("account deleted: ",username)

    cursor.close()
    connection.close()
    return

#returns list of users
def get_users():
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    users = cursor.execute("SELECT username FROM users").fetchall()

    cursor.close()
    connection.close()
    return users

#given a username, returns a dict of profile details
def get_profile(username):
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()
    userid = str(cursor.execute("SELECT rowid FROM users where username = (?)", (username,)).fetchall()[0][0])
    avatar = cursor.execute("SELECT avatar FROM profiles WHERE userid = (?)", userid).fetchall()[0][0]
    fname = cursor.execute("SELECT fname FROM profiles WHERE userid = (?)", userid).fetchall()[0][0]
    lname = cursor.execute("SELECT lname FROM profiles WHERE userid = (?)", userid).fetchall()[0][0]

    details = {
        "avatar": avatar,
        "fname": fname,
        "lname": lname,
        }

    cursor.close()
    connection.close()
    return details

#given a username and new name, updates the profile
def update_name(username,fname,lname):
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    userid = str(cursor.execute("SELECT rowid FROM users where username = (?)", (username,)).fetchall()[0][0])
    cursor.execute("UPDATE profiles SET fname = (?) WHERE userid = (?)",(fname, userid))
    connection.commit()
    cursor.execute("UPDATE profiles SET lname = (?) WHERE userid = (?)",(lname, userid))
    connection.commit()

    cursor.close()
    connection.close()
    return

#given a username and new password, updates the profile
def update_password(username,password):
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    salt = ''.join(random.choices(string.printable, k=10))
    hash = hashlib.sha256()
    hash.update(password.encode()+salt.encode())
    passwordHash = hash.hexdigest()

    cursor.execute("UPDATE users SET password = (?) WHERE username = (?)", (passwordHash,username))
    connection.commit()
    cursor.execute("UPDATE users SET salt = (?) WHERE username = (?)", (salt,username))
    connection.commit()

    cursor.close()
    connection.close()
    return

#given an image, updates the profile
def update_avatar(username, filename):
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    userid = str(cursor.execute("SELECT rowid FROM users where username = (?)", (username,)).fetchall()[0][0])
    cursor.execute("UPDATE profiles SET avatar = (?) WHERE userid = (?)", (filename,userid))
    connection.commit()
    display() #------------------------------------------------------------
    cursor.close()
    connection.close()
    return

#displays stuff in databases
def display():
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()
    print(cursor.execute("SELECT * FROM users").fetchall())
    print(cursor.execute("SELECT * FROM profiles").fetchall())
    cursor.close()
    connection.close()
    return

#checks if a username is in the users database
def check_exists(username):
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    data = (username,)
    alreadyexists = cursor.execute("SELECT username FROM users WHERE username = (?)", data).fetchall()
    if alreadyexists != []:
        cursor.close()
        connection.close()
        return True

    cursor.close()
    connection.close()
    return False

#-------------- stuff for testing
# init()
# user_register("yrral","password")
# get_users()
# display()
# update_name("bob","bobby","baddy")
# update_password("bob","notpassword")
# display()
# delete_account("bob")
# user_login("bob","password")
# display()
# delete_account("bob")
# display()
# get_profile("test")