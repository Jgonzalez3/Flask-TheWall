from flask import Flask, redirect, render_template, request, session, flash
from mysqlconnection import MySQLConnection
import md5, re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9.+_-]+\.[a-zA-Z]+$')

app = Flask(__name__)
app.secret_key = "secret"
mysql = MySQLConnection(app, 'wall')
@app.route("/")
def index():
    return render_template("wallhome.html")

@app.route('/register', methods=['POST'])
def create_user():
    errors = []
    firstname = request.form['first_name']
    lastname = request.form['last_name']
    session['lastname'] = lastname
    email = request.form['email']
    password = md5.new(request.form['password']).hexdigest()

    email_query = "SELECT * FROM users WHERE users.email = :email"
    email_data = {'email': email}
    emailcheck = mysql.query_db(email_query, email_data)
    # print emailcheck

    if len(request.form['first_name']) < 2:
        errors.append("First Name must have at least 2 characters")
    for i in range(0,len(firstname)):
        if firstname[i] == "1" or firstname[i] == "2" or firstname[i] == '3' or firstname[i] == '4' or firstname[i] == '5' or firstname[i] == '6' or firstname[i] == '7' or firstname[i] == '8' or firstname[i] == '9' or firstname[i] == '0':
            errors.append("First Name can only contain letters")
    if len(request.form['last_name']) < 2:
        errors.append("Last Name must have at least 2 characters")
    for i in range(0,len(lastname)):
        if lastname[i] == "1" or lastname[i] == "2" or lastname[i] == '3' or lastname[i] == '4' or lastname[i] == '5' or lastname[i] == '6' or lastname[i] == '7' or lastname[i] == '8' or lastname[i] == '9' or lastname[i] == '0':
            errors.append("Last Name can only contain letters")
    if len(emailcheck) > 0:
        errors.append("Email already in use")
    if not EMAIL_REGEX.match(request.form['email']):
        errors.append("Email is Invalid")
    if len(request.form["password"]) < 8:
        errors.append("Password Must Contain More than 8 Characters")
    if request.form["pw_confirm"] != request.form["password"]:
        errors.append("Passwords Do Not Match Re-enter")
    if len(errors) > 0:
        for error in errors:
            flash(error)
        return redirect("/")

    insert_query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (:first_name, :last_name, :email, :password, NOW(), NOW())"
    data = {'first_name': firstname, 'last_name': lastname, 'email': email, 'password': password }
    mysql.query_db(insert_query, data)
    
    return redirect("/wall")

@app.route("/login", methods = ['POST'])
def login():
    errors = []
    email = request.form['email']
    password = md5.new(request.form['password']).hexdigest()
    query = "SELECT * FROM users WHERE users.email = :email AND users.password = :password"
    data = {'email': email, 'password': password }
    valid = mysql.query_db(query, data)
    session["name"] = valid[0]["first_name"]
    session["userid"] = valid[0]["id"]
    # print"log in", valid
    # print data
    if valid == []:
        errors.append("Invalid Email or Password")
    elif password == valid[0]['password'] and email == valid[0]["email"]:
        return redirect("/wall")
    if len(errors) > 0:
        for error in errors:
            flash(error)
        return redirect("/")

@app.route("/wall")
def wall():
    query_m = "SELECT messages.id as messagesid, messages.messages, DATE_FORMAT(messages.created_at, '%M %D %Y') as messagedate, concat(users.first_name, ' ', users.last_name) as messagename FROM users JOIN messages ON users.id = messages.users_id ORDER BY messages.created_at DESC"
    query_c = "SELECT comments.comment, DATE_FORMAT(comments.created_at, '%M %D %Y') as commentdate, messages.id as messagesid, concat(users.first_name, ' ', users.last_name) as commentname FROM users RIGHT JOIN comments ON users.id = comments.users_id JOIN messages on comments.messages_id = messages.id ORDER BY comments.created_at ASC"
    query_messages = mysql.query_db(query_m)
    # print query_messages[0]["messagesid"]
    query_comments = mysql.query_db(query_c)
    # print query_comments
    # print query_comments[0]["messagesid"]
    # print query_comments[1]
    # print query_messages
    return render_template("wall.html", allmessages=query_messages, allcomments = query_comments)

@app.route("/postmessage", methods = ["POST"])
def message():
    message = request.form["message"]
    usersid = request.form["usersid"]
    insert_query = "INSERT INTO messages (messages, created_at, updated_at, users_id) VALUES (:message, NOW(), NOW(), :usersid)"
    # print "message query", insert_query
    data = {'message': message, 'usersid': usersid}
    # print "message data", data
    # print "message request from form", message
    insert_message = mysql.query_db(insert_query, data)

    # print "insert_message", insert_message
    return redirect("/wall")

@app.route("/postcomment", methods = ["POST"])
def postcomment():
    comment = request.form["comment"]
    messageid = request.form['messageid']
    usersid = request.form["usersid"]
    # print "comment:", comment
    # print "messageid:", messageid
    # print "usersid:", usersid 

    insert_query = "INSERT INTO comments (comment, created_at, updated_at, messages_id, users_id) VALUES (:comment, NOW(), NOW(), :messageid, :usersid)"
    # print "comment query:", insert_query
    data = {'comment': comment, 'usersid': usersid, 'messageid': messageid}
    # print "comment data:", data
    # print "messageid:", messageid
    # print "usersid:", usersid
    insert_comment = mysql.query_db(insert_query, data)
    return redirect("/wall")
@app.route("/logout", methods=["POST"])
def logout():
    # print session
    for key in session.keys():
        session.pop(key)
    return redirect("/")
app.run(debug=True)

