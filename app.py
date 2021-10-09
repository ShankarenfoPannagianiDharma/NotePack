from logging import error
from flask import Flask, request, redirect, flash, render_template
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
        return redirect("/Main")
    else:
        flash('User not found')
        return redirect('/')

@app.route("/Main")
def mainView():
    return render_template("Main.html")
@app.route('/ItemTables')
def ItemTables():
    return render_template('ItemTables.html')
@app.route('/Chat')
def Chat():
    return render_template('Chat.html')
@app.route('/Notes')
def Notes():
    return render_template('Notes.html')
@app.route('/Profile')
def Profile():
    return render_template('Profile.html')
@app.route('/Reminders')
def Reminders():
    return render_template('Reminders.html')

    