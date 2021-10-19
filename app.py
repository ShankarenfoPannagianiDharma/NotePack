import os, shutil ,re
from flask import Flask, request, redirect, flash, render_template, session, send_file
from flaskext.mysql import MySQL

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1
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

@app.after_request
def add_header(response):
    # response.cache_control.no_store = True
    if 'Cache-Control' not in response.headers:
        response.headers['Cache-Control'] = 'no-store'
    return response

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
    
    accImageB64 = request.form["ImageB64"]

    #VALIDATION
    #REGEX Validation needs reworking to fit python
    emailValidation = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if(accName==''):
        flash('Please enter your account\'s name\/handle.')
        return redirect("/Registration")
    elif not re.match("^[a-zA-Z0-9_.-]+$", accName):
        flash('Account\'s name/handle should not have symbols other than "_", "." and "-"')
        return redirect("/Registration")
    # else if(!preg_match($letters,$accName)) {
    #     header("Location: Registration.html?message=AccNOnlyAlph");
    # }
    elif(accMail==''):
        flash('Please enter your E-Mail.')
        return redirect("/Registration")
    elif not (re.fullmatch(emailValidation, accMail)):
        flash('Please enter a valid email.')
        return redirect("/Registration")
    elif(accPass==''):
        flash('Please enter your password.')
        return redirect("/Registration")
    #  password restrictions not necessary 
    # else if(!preg_match($pwd_expression,$accPass)){
    #     header("Location: Registration.html?message=PssInv");
    # }
    elif(accImageB64=='' or accImageB64 == None):
        flash('Please upload an image.')
        return redirect("/Registration")
    elif(len(accPass) < 6):
        flash('Password should be more than 6 characters.')
        return redirect("/Registration")
    elif(len(accPass) > 12):
        flash('Password should be less than 12 characters.')
        return redirect("/Registration")
    
     #Generate image name
    accImage = accName.replace(" ","_").replace(".","_")+"_user_image"

    #Save image
    convert_and_save(accImageB64,accImage);
    
    #connect to db
    conn = mysql.connect()
    cursor =conn.cursor()

    try:
        cursor.execute("INSERT INTO users (Handle, Password, Email, Image) VALUES ('"+accName+"','"+accPass+"','"+accMail+"','"+accImage+".jpg')")
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
    accImageB64 = request.form['ImageB64']  

    #connect to db
    conn = mysql.connect()
    cursor =conn.cursor()
   
    if accPass is not None and accPass != '':
        cursor.execute("SELECT * FROM users WHERE Handle='"+accName+"' AND Password='"+accPass+"';")
        data = cursor.fetchone()

        if(data is not None):
            session['accountID'] = data[0]
            return redirect("/Main")
        else:
            flash('User not found')
            return redirect('/')

    cursor.execute("SELECT * FROM users WHERE Handle='"+accName+"';")
    data = cursor.fetchone()

    if(data is not None):
        convert_and_save(accImageB64,accName+"_attempt_login")
        if compare(accName+"_attempt_login.jpg", data[4]):
            session['accountID'] = data[0]
            return redirect("/Main")
        else:
            flash('User not recognized')
            return redirect('/')
    else:
        flash('User not found')
        return redirect('/')

@app.route("/Main")
def mainView():
    #return render_template("Main.html")    
    if session['accountID'] == None:
        return redirect("/index")
    else:
        return render_template("Main.html")
#this is a pit-stop to reset session CD->redirects to ItemTablesList
@app.route('/ItemTables')
def ItemTables():
    chckDir(session['accountID'])
    session['currentDirectory'] = "UserRepos/"+str(session['accountID'])+"/Files"
    return redirect("/ItemTablesList")

#actual list of items in (session directory)
@app.route('/ItemTablesList')
def ItemTablesList():
    #get list of items in file repository
    isRoot = True
    if(session['currentDirectory'] != "UserRepos/"+str(session['accountID'])+"/Files"):
        isRoot = False

    filesList = list()
    foldrList = list()
    # separate directories and files
    for entry in os.scandir(session['currentDirectory']):
        if entry.is_dir():
            foldrList.append(entry.name)
        else:
            filesList.append(entry.name)

    #serve template with params:list of files, list of folders, boolean if it is root
    return render_template('ItemTables.html', files=filesList, foldrs=foldrList, isRoot=isRoot)

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
            file.save(session['currentDirectory']+"/"+file.filename.replace(" ","_"))
        else:
            print("NO FILE!")
    return ('', 204)

@app.route("/DowFile", methods=["POST"])
def dowFile():
    return send_file(session['currentDirectory']+"/"+request.form['targetFile'],as_attachment=True)

@app.route("/DelFile",methods=["POST"])
def delFile():
    os.remove(session['currentDirectory']+"/"+request.form['targetFile'])
    return ('', 204)

@app.route("/newFolder", methods=["POST"])
def createFolder():
    folderName = request.form['newFName']
    if not os.path.exists(session['currentDirectory']+"/"+folderName):
        os.makedirs(session['currentDirectory']+"/"+folderName)
    return ('', 204)

@app.route("/moveCD", methods=["POST"])
def redirectCD():
    nextDir = request.form['movement']
    if(nextDir == "..."):
        session['currentDirectory'] = os.path.dirname(session['currentDirectory'])
    else:
        session['currentDirectory'] += "/"+nextDir
    return ('', 204)

@app.route("/DelFolder", methods=["POST"])
def deleteFolder():
    targetDir = session['currentDirectory'] + "/"+request.form['targetFolder']
    if len(os.listdir(targetDir)) == 0:
        print("Directory is empty")
        os.rmdir(targetDir)
    else:    
        print("Directory is not empty")
        shutil.rmtree(targetDir)
    return ('', 204)

#method to make directory of user id(int) if does not exist.
def chckDir(id):
    if not os.path.exists("UserRepos/"+str(id)+"/Files/"):
        os.makedirs("UserRepos/"+str(id)+"/Files/")
        
####
## START
####
import base64 
import boto3

import creds
from botocore.exceptions import ClientError, PaginationError
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime   
from flask import session, url_for

@app.route("/uploadImage", methods=["POST"])
def uploadImage():
    convert_and_save(request.form["base64"],request.form["name"])
    return "Image saved!"

@app.route('/change_picture', methods=["POST"])
def change_picture():
    if(session['accountID'] is None or session['accountID'] == ''):
        flash('No session')
        return redirect('/')

    accImageB64 = request.form["ImageB64"]
    #connect to db, get user details
    conn = mysql.connect()
    cursor =conn.cursor()
    cursor.execute("SELECT * FROM users WHERE ID_User="+str(session['accountID'])+";")
    data = cursor.fetchone()
    convert_and_save(accImageB64,data[4].split(".")[0])
    flash('Image changed')
    return redirect(url_for('Profile', userData=data))

def convert_and_save(b64_string, name):
    filename="static\\userimages\\"+name+".jpg"
    imgdata = base64.b64decode(b64_string)
    with open(filename, 'wb') as f:
        f.write(imgdata)


def compare(source_image_name, target_image_name):
    rekognition_client = boto3.client(
        'rekognition',
        aws_access_key_id=creds.rekognition['access_key_id'],
        aws_secret_access_key=creds.rekognition['secret_access_key'],
        region_name=creds.rekognition['region'],
    )
    
    FOLDER_NAME = 'static/userimages'
    source_image_path = '%s/%s' % (FOLDER_NAME, source_image_name)
    target_image_path = '%s/%s' % (FOLDER_NAME, target_image_name)

    source_bytes = open(source_image_path, 'rb')
    target_bytes = open(target_image_path, 'rb')


    try:
        response = rekognition_client.compare_faces(
            SourceImage={'Bytes':source_bytes.read()},
            TargetImage={'Bytes':target_bytes.read()},
            SimilarityThreshold=10,
        )
        print(response)
        if(len(response["FaceMatches"]) != 0):
            return True
        else:
            return False
    except ClientError as e:
        print(e)
        return False

def get_image(filename):
    with open(filename, "rb") as cf:
        base64_image=base64.b64encode(cf.read())
        decoded = base64.decodebytes(base64_image)
        return decoded

        


####
## END
####        
        
        
        
        
        
        
        
        
        
        
        
