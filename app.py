from flask import Flask, send_file, request, url_for, redirect, Blueprint, render_template, abort, make_response
from jinja2 import TemplateNotFound
# import games
import uuid
import os
import database
import redis
from werkzeug.utils import secure_filename
from flask_sse import sse
import Roulette

#sudo service redis-server restart
#start the redis server with this

database.init()
r = redis.Redis(host='localhost', port=6379, decode_responses=True)
#more databases for games and stuff

runningGames = {}
#folder to store profile pictures
UPLOAD_FOLDER = os.path.join("static","avatars")
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def loggedIn(cookies: dict) -> bool:
    '''
    cookies: the request cookies

    Returns True if the user is logged in

    Returns False if the user is not logged in
    '''
    if request.cookies.get('userID') == None:
        #no userID
        return False
    if r.get(request.cookies.get('userID')) == None:
        #invalid userID
        return False
    return True


def username(cookies: dict) -> str:
    '''
    cookies: the request cookies

    Returns the username of the user
    Returns None if user is not logged in
    '''
    return r.get(request.cookies.get('userID'))

#create a blueprint
game_print = Blueprint('game_print', 'game.roulette')

@game_print.route('/<gameid>', methods=['GET','PUT'])
def game(gameid):
    print("test")
    #check if logged in
    #check if game with id exists
    #check if player in game(use cookies to get username)
    #check if game is still in progress
    if request.method == 'GET':
        return
        # return render_template("roulette.j2", player = self_username, opponent = opp_username)

    #check if logged in
    #check if game with id exists
    #check if player in game
    if request.method == 'PUT':
        return


#create Flask object
app = Flask(__name__, template_folder = "templates")
app.register_blueprint(game_print, url_prefix='/play')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["REDIS_URL"] = "redis://localhost"
app.register_blueprint(sse, url_prefix='/stream')

#creates a route
@app.route("/", methods=['GET'])
def index():
    # if user is not logged in redirect to login page     ----------  has bug
    #check for cookie, if exists, redirect to /user/profile, else redirect to login
    try:
        if r.get(request.cookies.get('userID')) != None:
            username = r.get(request.cookies.get("userID")) 
            return redirect(f"/{username}/profile",username) 
        return redirect(url_for("login"))
    except:
        return redirect(url_for("login")), 301

@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template("login.j2",error="")

    if request.method == 'POST':
        username = request.form.get('Username')
        password = request.form.get('Password')
        mode = request.form.get('mode')
        print("Username:", username, " Password:", password, " Mode:", mode)
        if mode == "Register":
            if database.user_register(username,password): #if registering is a success then count them as logged in
                #insert session stuff
                userid = str(uuid.uuid4())
                res = make_response(redirect(f"/{username}/profile"))
                res.set_cookie('userID', userid)
                r.set(userid,username) #store cookie in redis
                return res
            else: #return template with error message
                return render_template("login.j2",error="Account already exists. The username must be unique")

        if mode == "Login":
            if database.user_login(username,password):
                #insert session stuff
                userid = str(uuid.uuid4())
                res = make_response(redirect(f"/{username}/profile"))
                res.set_cookie('userID', userid)
                r.set(userid,username) #store cookie in redis
                return res
            else: #return template with error message
                return render_template("login.j2",error="Incorrect username or password")

@app.route("/logout", methods=['POST']) #user profile
def logout():
    print("logout triggered")
    try:
        #invalidate cookie and redirect to the /login route
        r.delete(request.cookies.get('userID'))
        print("logged out")
        return redirect(url_for("login")) 
    except:
        print("not logged in")
        return redirect(url_for("login")) 


# display list of profiles when logged in
@app.route("/profiles", methods=['GET']) 
def profile():
    try:
        #checks if user is logged in or not
        cookie = r.get(request.cookies.get('userID'))
        if cookie != None:
            userlist = database.get_users()
            userdict = {}
            for x in range(len(userlist)):
                userdict[userlist[x][0]] = "/"+userlist[x][0]+"/profile"

            return render_template("profile_list.j2", dict = userdict)
        return redirect(url_for("login"))
    except:
        print("not logged in")
        return redirect(url_for("login"))
    
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/<user>/profile", methods=['GET','PUT','DELETE']) #user profile
def account(user):
    if request.method == 'GET': 
        #check if user exists
        if database.check_exists(user):
            #check for cookie
            try:
                if r.get(request.cookies.get('userID')) == user:
                    print("logged in profiles page")
                    return render_template("profile.j2",username = user,loggedin = "true",error = "")

                #template with no edit option
                print("not logged in profiles page")
                return render_template("profile.j2",username = user,loggedin = "false",error = "")
            except:
                #template with no edit option
                print("not logged in profiles page")
                return render_template("profile.j2",username = user,loggedin = "false",error = "")
            
        else:
            return send_file("static/404.html")
    
    if request.method == 'PUT':
        status = "ok"
        returnData = "data"
        
        def error(message):
            status = "error"
            returnData = message
            return {
                "status": status,
                "data": returnData
            }

        #check for cookie
        try:
            cookie = r.get(request.cookies.get('userID'))
        except:
            print("not logged in")
            database.display()
            return error("data")

        #check for json
        try:
            request_data = request.get_json()
        except:
            if cookie == user:
                print("user is logged in")
                data = request.files

                # if there is no file, it likely wasn't intended for this function
                if 'avatar' not in data:
                    print("file not in data")
                    return error("No JSON provided")
                
                file = data['avatar']
                # If the user does not select a file, the browser submits an
                # empty file without a filename.
                if file.filename == '':
                    print('No selected file')
                    return error('no selected file')

                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    database.update_avatar(user,"/static/avatars/"+filename)
                    return {
                        "status": "ok",
                        "data": ""
                    }  
            else:
                print("logged in as wrong person")
                return error("data")
            
            return error("No JSON provided")
        
        #check for and get action
        if "action" not in request_data:
            print("action is missing")
            return error("Action is Missing")

        action = request_data['action']
        print("action is present: ", action)

        #get: give profile details
        if action == "get":
            returnData = database.get_profile(user)
            print("return data: ",returnData)
            return{
                "status": status,
                "data": returnData
            }  
        
        #update: updates profile name and password details
        if action == "update":
            #Make sure user is logged in correctly
            if cookie == user:
                print("user is logged in")
                data = request_data['data']
                print(data)

                #check that fname and lname arent empty
                if data['fname'].strip() != "" and data['lname'].strip() != "":
                    #check that password and cpassword are equal and not empty
                    if data['password'].strip() != "" and data['password'].strip() == data['cpassword'].strip():
                        database.update_password(user,data['password'].strip())
                        print("updated password")

                    #error if password and cpassword don't match
                    elif data['password'].strip() != "" and data['password'].strip() != data['cpassword'].strip():
                        return error("password and confirm password have to match")
                    
                    database.update_name(user,data['fname'].strip(),data['lname'].strip())
                    print("updated username")
                    return {
                        "status": "ok",
                        "data": ""
                    }  

                return error("First and last name can't be empty")
                
            else:
                print("logged in as wrong person")
                return error("data")
            
    if request.method == 'DELETE':
        print("delete received")
        try:
            #check for cookie
            cookie = r.get(request.cookies.get('userID'))
            if cookie == user:
                #delete account and cookie
                database.delete_account(user)
                r.delete(request.cookies.get('userID'))
                
                return redirect(url_for("deleted"),code=303)
            else:
                print("logged in as wrong person")
                return error("set the status!")
        except:
            print("not logged in")
            return error("data")

#transition screen when account deleted
@app.route("/deleted", methods=['GET','DELETE']) 
def deleted():
    print("deleted page")
    return render_template("deleted.j2"), {"Refresh": "5; url=/login"}

#playing the game
@app.route("/play", methods=['GET','PUT','POST']) #user profile
def play():
    #find the specific game currently being played
    #roulette object for logic
    
    return render_template("roulette.j2")

#boolean controlling whether to queue or not
print("initialized random stuff")
playerWaiting = False
playerUsername = ""
#searching for people to play against
@app.route("/queue", methods=['GET','PUT','POST']) #user profile
def queue():
    global playerWaiting
    global playerUsername
    #include queue timer
    #on client side(JavaScript), can have a async function...
    #...that waits for server to say if a game has been found, etc.
    #check for disconnect
    if not loggedIn(request.cookies):
        #user not logged in, so we make them log in
        return redirect(url_for("login"))
    if not playerWaiting:
        #no player currently in queue, add this player to the queue
        playerUsername = username(request.cookies)
        playerWaiting = True
        return render_template("queue.j2")
    else:
        #we have a player in the queue, so we match them together
        gameID = str(uuid.uuid4())
        game = Roulette.Roulette(playerUsername, username(request.cookies))
        #the queued player becomes player 1, the newly joined player becomes player 2
        runningGames[gameID] = game
        playerWaiting = False
        sse.publish({"message": gameID}, type='matchFound')
        #give player 1 a notification that a game was found

        parameters = "?ID="+gameID
        return redirect(url_for("play")+parameters)



#test game page
@app.route("/testgame", methods=['GET'])
def testgame():
    return render_template("roulette.j2", player = "self", opponent = "opponent")

@app.errorhandler(404)
def notfound(e):
    return send_file("static/404.html")


@app.route("/debug")
def debug():
    return render_template("queue.j2")


@app.route('/send')
def send_message():
    sse.publish('{"message": "foobar!"}', type='matchFound')
    return "Message sent!"



#runs the server
app.run(port=8080)