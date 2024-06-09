# Author: Prof. MM Ghassemi <ghassem3@msu.edu>
from flask import current_app as app, jsonify, send_from_directory
from flask import render_template, redirect, request, session, url_for, copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect
from .utils.database.database  import database
from werkzeug.datastructures   import ImmutableMultiDict
from pprint import pprint
import json
import random
import functools
from . import socketio
import datetime
db = database()


#######################################################################################
# AUTHENTICATION RELATED
#######################################################################################
def login_required(func):
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        if "email" not in session:
            return redirect(url_for("login", next=request.url))
        return func(*args, **kwargs)
    return secure_function

def getUser():
    return db.reversibleEncrypt('decrypt', session['email']) if 'email' in session else 'Unknown'

@app.route('/login')
def login():
    return render_template('login.html', title = "Login", user = getUser(), attempts = db.login_attempts)

@app.route('/logout')
def logout():
    session.pop('email', default=None)
    return redirect('/')

@app.route('/processlogin', methods = ["POST","GET"])
def processlogin():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    status =  db.authenticate(email=form_fields['email'], password=form_fields['password'])
    # if the login is sucessful
    if status['success'] == 1:
        session['email'] = db.reversibleEncrypt('encrypt', form_fields['email'])
    return json.dumps(status)
 
#######################################################################################
# CHATROOM RELATED
#######################################################################################
@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html', user=getUser(), title = "Chat")

@socketio.on('joined', namespace='/chat')
def joined(message):
    join_room('main')
    #if the user is the owner email, then send the message with that formatting, otherwise use the other formatting
    if getUser() == "owner@email.com":
        emit('status', {'msg': getUser() + ' has entered the room.', 'style': 'width: 100%;color:blue;text-align: right'}, room='main')
    else:
        emit('status', {'msg': getUser() + ' has entered the room.', 'style': 'width: 100%;color:gray;text-align: left'}, room='main')

@socketio.on('leave', namespace='/chat')
def leave(message):
    leave_room('main')
    #if the user is the owner email, then send the message with that formatting, otherwise use the other formatting
    if getUser() == "owner@email.com":
        emit('status', {'msg': getUser() + ' has left the room.', 'style': 'width: 100%;color:blue;text-align: right'}, room='main')
    else:
        emit('status', {'msg': getUser() + ' has left the room.', 'style': 'width: 100%;color:gray;text-align: left'}, room='main')

@socketio.on('send', namespace = '/chat')
def send(message):
    join_room('main')
    #if the user is the owner email, then send the message with that formatting, otherwise use the other formatting
    if getUser() == "owner@email.com":
        emit('status', {'msg': message, 'style': 'width: 100%;color:blue;text-align: right'}, room='main')
    else:
        emit('status', {'msg': message, 'style': 'width: 100%;color:gray;text-align: left'}, room='main')


#######################################################################################
# Final exam
#######################################################################################

@app.route('/wordle')
@login_required
def wordle():
    # get the user
    user = getUser()

    # get the word
    db.getword()

    # TRY to clear the leaderboard everytime the user visits a page, leaderboard should only clear if the date changes
    db.clearLeaderboard()

    # track amount of times user has visited the site
    visits = db.timesVisited(user)

    # indicate that the user has viisted the site by adding to the data table
    db.addVisit(user)

    # get word length
    word_length = len(db.word_of_the_day)

    # get leaderboard data
    leaderboard = getLeaderboardData()
    return render_template('wordle.html',  user=getUser(), title="Wordle", word_length = word_length, visits = visits, leaderboard = leaderboard)

#process a used signing up
@app.route('/process_sign_up', methods = ["POST","GET"])
def process_sign_up():
    # very similar to the process login, it just checks if the sign up attempt is valid 
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    check_sign_up = db.createUser(email=form_fields['email'], password=form_fields['password'], role='guest')
    if check_sign_up['success'] == 0:
        db.sign_up_attempt = 1
    else:
        db.sign_up_attempt = 0
    return json.dumps(check_sign_up) 

@app.route('/signup')
def signup():
    return render_template('signup.html',  user=getUser(), title="SignUp", attempted_sign_up = db.sign_up_attempt)

# A different page that is pretty much the same as the login.html I just want to make it visually apparent the sign up was a success
@app.route('/signupsuccessful')
def signupsuccessful():
    return render_template('signupsuccessful.html',  user=getUser(), title="Login", attempts = db.login_attempts)

# get the hidden_word stored in the database
def generate_hidden_word():
    return db.word_of_the_day

# a route that will allow me to fetch the hidden word from the database
@app.route('/get_hidden_word')
def get_hidden_word():
    hidden_word = generate_hidden_word()
    return jsonify({'hidden_word': hidden_word})

# a route to allow me to add a user and the time it took for them to complete the game to the data table
@app.route('/getwordletime', methods = ['POST','GET'])
def getwordletime():
    if request.method == 'POST':
        time = request.get_json()
        db.addToLeaderboard(getUser(), time)
        return jsonify({'time': time})
    else:
        return jsonify({'success': 1})

# a route to allow me to fetch the leaderboard data from the data base
@app.route('/getleaderboarddata', methods = ['POST', 'GET'])
def getLeaderboardData():
    data = db.getLeaderboardData()
    sorted_data = sorted(data.items(), key=lambda x: x[1])
    return sorted_data[:5]

# a route to indicate that the user has now completed a game before today
@app.route('/markgamecompleted', methods = ['POST', 'GET'])
def markgamecompleted():
    db.completedGame(getUser())
    return jsonify({'success': 1})

# a route to allow me to fetch whether or not the user has played today
@app.route('/checkgamecompleted')
def checkgamecompleted():
    return jsonify({'game_completed' :db.getCompletedGame(getUser())})

#######################################################################################
# OTHER
#######################################################################################
db = database()

@app.route('/')
def root():
    return redirect('/home')

@app.route('/home')
def home():
    return render_template('home.html',  user=getUser(), title="Home")

@app.route('/projects')
def projects():
    return render_template('projects.html', user=getUser(), title="Projects")

@app.route('/piano')
def piano():
    return render_template('piano.html',  user=getUser(), title="Piano")

@app.route('/resume')
def resume():
    data = db.getResumeData()
    return render_template('resume.html',  user=getUser(), data = data, title = "Resume")

@app.route('/feedback', methods = ['POST'])
def feedback():
    feedback = request.form
    #convert the request to a dict
    feedback_data = feedback.to_dict()
    data_keys = list(feedback_data.keys()) #grab the keys
    data_values = [list(feedback_data.values())] #grab the values and make them in a nested list
    db.insertRows('feedback', data_keys, data_values) #call insert rows with the gven parameters
    data = db.getFeedback()
    return render_template('feedback.html',user = getUser(), title = "Feedback", data = data)

@app.route("/static/<path:path>")
def static_dir(path):
    return send_from_directory("static", path)

@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    return r
