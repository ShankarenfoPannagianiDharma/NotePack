import os
from flask import Flask, request, redirect, flash, render_template, session, send_file
from flaskext.mysql import MySQL

app = Flask(__name__)
app.secret_key = "SCRTKY"
if __name__ == '__main__':
    app.debug = True
    app.run()

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'notespack_db'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

@app.route("/index")
@app.route("/")
def index():
    session['accountID'] = ""
    return render_template("index.html")

@app.route("/Registration")
def registrationView():
    return render_template("Registration.html")

@app.route("/operation_register", methods=["POST"])
def registeroperation():
    accName = request.form["AccountName"]
    accMail = request.form["EMail"]
    accPass = request.form["Password"]

    #VALIDATION
    #REGEX Validation needs reworking to fit python
    pwd_expression = "/^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-])/"
    letters = "/^[A-Za-z]+$/"
    filter = "/^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/"

    if(accName==''):
        flash('Please enter your account\'s name\/handle.')
        return redirect("/Registration")
    # else if(!preg_match($letters,$accName)) {
    #     header("Location: Registration.html?message=AccNOnlyAlph");
    # }
    elif(accMail==''):
        flash('Please enter your E-Mail.')
        return redirect("/Registration")
    # else if (!preg_match($filter,$accMail)) {
    #     header("Location: Registration.html?message=accMInv");
    # }
    elif(accPass==''):
        flash('Please enter your password.')
        return redirect("/Registration")
    #  password restrictions not necessary 
    # else if(!preg_match($pwd_expression,$accPass)){
    #     header("Location: Registration.html?message=PssInv");
    # }
    elif(len(accPass) < 6):
        flash('Password should be more than 6 characters.')
        return redirect("/Registration")
    elif(len(accPass) > 12):
        flash('Password should be less than 12 characters.')
        return redirect("/Registration")

    #connect to db
    conn = mysql.connect()
    cursor =conn.cursor()

    try:
        cursor.execute("INSERT INTO users (Handle, Password, Email) VALUES ('"+accName+"','"+accPass+"','"+accMail+"')")
        conn.commit()
        cursor.execute("SELECT ID_User FROM users WHERE Handle='"+accName+"' AND Password='"+accPass+"';")
        data = cursor.fetchone()

        session['accountID'] = data[0]
        return redirect("/Main")
    except Exception as e:
        flash('That name already exists.'+str(e))
        return redirect("/Registration")


@app.route("/operation_login", methods=["POST"])
def loginperation():
    accName = request.form['accountName']  
    accPass = request.form['accountPass']  

    #connect to db
    conn = mysql.connect()
    cursor =conn.cursor()

    cursor.execute("SELECT * FROM users WHERE Handle='"+accName+"' AND Password='"+accPass+"';")
    data = cursor.fetchone()

    if(data is not None):
        session['accountID'] = data[0]
        return redirect("/Main")
    else:
        flash('User not found')
        return redirect('/')

@app.route("/Main")
def mainView():
    return render_template("Main.html")
@app.route('/ItemTables')
def ItemTables():
    #get list of items in file repository
    chckDir(session['accountID'])
    userFiles = os.listdir("UserRepos/"+str(session['accountID'])+"/Files")
    return render_template('ItemTables.html', files=userFiles)
@app.route('/Chat')
def Chat():
    return render_template('Chat.html')
@app.route('/Notes')
def Notes():
    return render_template('Notes.html')
@app.route('/Profile')
def Profile():
    if(session['accountID'] is None or session['accountID'] == ''):
        return redirect('/')

    #connect to db, get user details
    conn = mysql.connect()
    cursor =conn.cursor()
    cursor.execute("SELECT * FROM users WHERE ID_User="+str(session['accountID'])+";")
    data = cursor.fetchone()

    return render_template('Profile.html', userData=data)
@app.route('/Reminders')
def Reminders():
    return render_template('Reminders.html')

    
@app.route('/POSTUploadFile', methods=["POST"])
def POSTFile():

    #Check and make directory if repo does/does not exists
    chckDir(session['accountID'])
    for file in request.files.getlist('file'):
        if file.filename != '':
            #also replace whitespaces with '_', file pathing has trouble with whitespace
            file.save("UserRepos/"+str(session['accountID'])+"/Files/"+file.filename.replace(" ","_"))
    return redirect('/ItemTables')

@app.route("/DowFile", methods=["POST"])
def dowFile():
    return send_file("UserRepos\\"+str(session['accountID'])+"\\Files\\"+request.form['targetFile'])

@app.route("/DelFile",methods=["POST"])
def delFile():
    os.remove("UserRepos\\"+str(session['accountID'])+"\\Files\\"+request.form['targetFile'])
    return redirect('/ItemTables')

#method to make directory of user id(int) if does not exist.
def chckDir(id):
    if not os.path.exists("UserRepos/"+str(id)+"/Files/"):
        os.makedirs("UserRepos/"+str(id)+"/Files/")