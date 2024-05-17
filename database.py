# this is SQLite3 database stuff
# might be commented properly

import string
import random
import sqlite3
import hashlib

#creates the users, profiles, and games tables
def init():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users
    (rowid INTEGER PRIMARY KEY, username TEXT, password TEXT, salt TEXT)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS profiles
    (rowid INTEGER PRIMARY KEY, userid INTEGER, fname TEXT, lname TEXT, avatar TEXT)""")
    #tracks games - can be used to find game and for match history
    cursor.execute("""CREATE TABLE IF NOT EXISTS games
    (gameid TEXT, player1 TEXT, player2 TEXT, status INTEGER)""")

    cursor.close()
    connection.close()
    return

def user_register(username:str, password:str) -> bool:
    '''
    username - the username of the person trying to register
    password - the password of the person trying to register
    returns True if successfully registered, returns False if not
    '''

    connection = sqlite3.connect("database.db")
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

#input: string username, string password
#attempts to login a user
#returns True if succesfully logged in, returns False if not
def user_login(username: str, password: str) -> bool:
    connection = sqlite3.connect("database.db")
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

#input string username
#deletes account with username string username
def delete_account(username: str):
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    
    #get rowid, delete from users table, then delete from profiles table
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
def get_users() -> list:
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    users = cursor.execute("SELECT username FROM users").fetchall()

    cursor.close()
    connection.close()
    return users

#input: string username
#given a username, returns a dict of profile details
#returns dict details
def get_profile(username: str) -> dict:
    connection = sqlite3.connect("database.db")
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

#input string username, string fname, string lname
#given a username and new name, updates the profile
def update_name(username: str,fname: str,lname: str):
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    userid = str(cursor.execute("SELECT rowid FROM users where username = (?)", (username,)).fetchall()[0][0])
    cursor.execute("UPDATE profiles SET fname = (?) WHERE userid = (?)",(fname, userid))
    connection.commit()
    cursor.execute("UPDATE profiles SET lname = (?) WHERE userid = (?)",(lname, userid))
    connection.commit()

    cursor.close()
    connection.close()
    return

#input: string username, string password
#given a username and new password, updates the profile
def update_password(username:str ,password:str ):
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    #create the salt, combine with password, hash the password
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

#input: string username, string filename
#given an image, updates the profile filepath
def update_avatar(username:str , filename:str ):
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    userid = str(cursor.execute("SELECT rowid FROM users where username = (?)", (username,)).fetchall()[0][0])
    cursor.execute("UPDATE profiles SET avatar = (?) WHERE userid = (?)", (filename,userid))
    connection.commit()
    display() #------------------------------------------------------------
    cursor.close()
    connection.close()
    return

#displays stuff in databases
#returns everything in the users, profiles, and games tables
def display():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    print(cursor.execute("SELECT * FROM users").fetchall())
    print(cursor.execute("SELECT * FROM profiles").fetchall())
    print(cursor.execute("SELECT * FROM games").fetchall())
    cursor.close()
    connection.close()
    return

#input string username
#checks if a username is in the users database
#returns true if in database, false if not
def check_exists(username:str) -> bool:
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    data = (username,)
    alreadyexists = cursor.execute("SELECT username FROM users WHERE username = (?)", data).fetchall()
    if alreadyexists != []:
        #array is not empty, so something exists
        cursor.close()
        connection.close()
        return True
    #array was empty, so nothing existed
    cursor.close()
    connection.close()
    return False

#input: string id, string player1, string player2
#stores information in the games database and sets its status to 0(ongoing)
def create_game(id:str,player1:str,player2:str):
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    data = (id,player1,player2,0)
    cursor.execute("INSERT INTO games (gameid, player1, player2, status) VALUES(?,?,?,?)", data)
    connection.commit()
    print("game created:",id,player1,player2,0)

    cursor.close()
    connection.close()

#Input: string id, string username
#checks if username is in game with gameid id
#returns True if yes, False if no or if no games have the id
def check_if_in_game(id:str, username:str) -> bool:
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    checker = cursor.execute("SELECT * FROM games WHERE gameid = (?)", (id,)).fetchall()
    # print("checker:",checker)

    cursor.close()
    connection.close()

    if len(checker) == 1:
        if checker[0][1] == username or checker[0][2] == username: #check if username in checker
            return True
        else:
            return False
    else:
        return False
    
#input: string id, int status
#updates status of game with string id with int status
def update_game(id:str,status:str):
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    cursor.execute("UPDATE games SET status = (?) WHERE gameid = (?)", (status, id))
    connection.commit()
    print("game updated:", id,status)

    cursor.close()
    connection.close()

#input: string id
#returns details(string id, string player1, string player2, int status) of the game with the id of string id
#returns error if multiple games with same id
def game_details(id:str) -> str:
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    checker = cursor.execute("SELECT * FROM games WHERE gameid = (?)", (id,)).fetchall()
    
    cursor.close()
    connection.close()
    
    if len(checker) == 1:
        return checker[0]
    else:
        return "error"

#-------------- stuff for testing
# init()
# create_game("idtest1","joe","bob")
# display()
# print(check_if_in_game("idtest1","bob"))
# update_game("idtest",2)
# display()
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
#print(type(get_users()))