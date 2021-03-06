import os, shutil ,re, flask
from flask import Flask, request, redirect, flash, render_template, session, send_file
from flaskext.mysql import MySQL
import re
import csv
from RecomendSys import BookRecommender

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
    elif(len(accName)>45):
        flash('Account name too long. Must be less than 45 characters.')
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
    elif(len(accMail)>45):
        flash('Email too long. Must be less than 45 characters.')
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
    # User can opt to NOT take image.
    # elif(accImageB64=='' or accImageB64 == None):
    #     flash('Please upload an image.')
    #     return redirect("/Registration")
    elif(len(accPass) < 6):
        flash('Password should be more than 6 characters.')
        return redirect("/Registration")
    elif(len(accPass)>45):
        flash('Password too long. Must be less than 45 characters.')
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

        #now save image (if given)
        if(accImageB64 != None or accImageB64!=''):
            #Generate image name
            accImage = accName.replace(" ","_").replace(".","_")+"_user_image"
            #Save image into static/userimages
            convert_and_save(accImageB64,accImage)

        return redirect("/Main")
    except Exception as e:
        flash('That name already exists.'+str(e))
        return redirect("/Registration")


@app.route("/operation_login", methods=["POST"])
def loginOperation():
    accName = request.form['accountName']  
    accPass = request.form['accountPass'] 
    accImageB64 = request.form['ImageB64']  
    #connect to db
    conn = mysql.connect()
    cursor =conn.cursor()

    #login with password (Priority)
    if accPass is not None and accPass != '':
        cursor.execute("SELECT * FROM users WHERE Handle='"+accName+"' AND Password='"+accPass+"';")
        data = cursor.fetchone()

        if(data is not None):
            session['accountID'] = data[0]
            return redirect("/Main")
        else:
            flash('User not found or password incorrect.')
            return redirect('/')

    elif(accImageB64 is not None and accImageB64 != ''):   #login with face recog
        print("face login")
        cursor.execute("SELECT * FROM users WHERE Handle='"+accName+"';")
        data = cursor.fetchone()

        if(data is not None):
            if not os.path.exists("static\\userimages\\"):
                os.makedirs("static\\userimages\\")
            filename="static\\userimages\\temp.jpg"
            imgdata = base64.b64decode(accImageB64)
            with open(filename, 'wb') as f:
                f.write(imgdata)
            if compare("temp.jpg"):
                session['accountID'] = data[0]
                return redirect("/Main")
            else:
                flash('User not recognized')
                return redirect('/')
        else:
            flash('User not found')
            return redirect('/')
    else:
        flash('Please enter password or take picture.')
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

    filesList = list()  #stores tuple [fileName.Ext, isText]
    foldrList = list()
    # separate directories and files
    for entry in os.scandir(session['currentDirectory']):
        if entry.is_dir():
            foldrList.append(entry.name)
        else:
            txtFile = False
            if entry.name.endswith(".txt"):
                txtFile = True
            filesList.append([entry.name,txtFile])

    #serve template with params:list of files, list of folders, boolean if it is root
    return render_template('ItemTables.html', files=filesList, foldrs=foldrList, isRoot=isRoot)

@app.route('/Chat')
def Chat():
    #connect to db
    conn = mysql.connect()
    cursor =conn.cursor()
    contactAbleUsers = list()
    #get list of all users that can be chatted with
    cursor.execute("SELECT * FROM users WHERE NOT ID_User="+str(session['accountID'])+";")
    data = cursor.fetchall()
    for entry in data:
        #if there are other users, add to list
        contactAbleUsers.append([entry[1]])

    #get list of rooms where user is owner of 
    roomsOwn = set()
    cursor.execute("SELECT * FROM `chatrooms` WHERE ID_RoomOwner="+str(session['accountID'])+";")
    data = cursor.fetchall()
    for entry in data:
        roomsOwn.add( tuple([entry[0],entry[1]]) )   #add (roomID, roomName)

    #get joined data of rooms and its members
    cursor.execute("SELECT * FROM `chatrooms` INNER JOIN `roommembers` ON chatrooms.ID_ChatRoom = roommembers.ID_ChatRoom;")
    data = cursor.fetchall()

    #get list of rooms where user is NOT an owner BUT a member of 
    roomsIn = set()
    for entry in data:
        if(entry[2] != session['accountID'] and entry[6] == session['accountID']):
            roomsIn.add( tuple( [entry[0],entry[1]] ) )    #add (roomID, roomName)

    #get list of rooms user can see (public) but not in or own
    #get all member rows where rooms are public
    cursor.execute("SELECT * FROM `chatrooms` INNER JOIN `roommembers` ON chatrooms.ID_ChatRoom = roommembers.ID_ChatRoom WHERE isPrivate=0")
    data = cursor.fetchall()
    groupedRooms = list()   #raw list of [roomID,roomOwner,[roomMembers]]
    tmpExistrooms = list()  #temporary list of roomID existing in groupList for reference
    tmpRoomnames = list()   #reference list of [roomID,roomName]
    for entry in data:
        if entry[0] not in tmpExistrooms:
            #new roomID, put into new grouped rooms
            tmpExistrooms.append(entry[0])
            members = list()
            members.append(entry[6])
            dataTuple = (entry[0],entry[2],members)
            groupedRooms.append(dataTuple)
            tmpRoomnames.append( (entry[0],entry[1]))
        else:
            #roomID exists. find index, append member into list
            tgtIndex = tmpExistrooms.index(entry[0])
            oldMembers = groupedRooms[tgtIndex][2]
            oldMembers.append( (entry[6]) )
            dataTuple = (entry[0],entry[2],oldMembers)
            groupedRooms[tgtIndex] = (dataTuple)
        #print(str(groupedRooms)) #View the grouping tuples
    
    #for each room group, check if user is member or owner
    #if they are, disqualify the room from legibility
    for roomGroup in groupedRooms:
        if roomGroup[1] == session['accountID']:    #if owner
            tmpExistrooms.remove(roomGroup[0])      #remove and proceed to next group
        else:                                       #else not owner
            for member in roomGroup[2]:             #check each member data
                if member == session['accountID']:  #if any one member is user, disqualify
                   tmpExistrooms.remove(roomGroup[0])
                   break                            #and end the loop 
    
    #get the names of rooms that are eligible
    roomsVisible = list()
    for room in tmpExistrooms:
        for roomName in tmpRoomnames:
            if(roomName[0] == room):
                roomsVisible.append( tuple( [room,roomName[1]] ) )

    return render_template('Chat.html',contactAbleUsers = contactAbleUsers,roomsOwn=roomsOwn,roomsIn=roomsIn,roomsVisible=roomsVisible)

@app.route('/Notes', methods=["GET","POST"])
def Notes():
    allFolders = list()
    originalFilename = ""
    originalLocation = ""
    originalText = ""

    #if editing a file
    if flask.request.method == 'POST':
        originalFilename = flask.request.values.get('targetFile').replace(".txt","")
        originalLocation = session['currentDirectory'].replace("UserRepos/"+str(session['accountID'])+"/Files","").replace("/","\\")+"\\"
        f = open(session['currentDirectory']+"\\"+flask.request.values.get('targetFile'))
        originalText = f.read()
    
    for x in os.walk("UserRepos\\"+str(session['accountID'])+"\\Files"):
        dir = x[0].replace("UserRepos\\"+str(session['accountID'])+"\\Files","")
        allFolders.append(dir+"\\")
    return render_template('Notes.html', allFolders = allFolders, originalFilename = originalFilename, originalLoc = originalLocation, originalText=originalText)

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

@app.route('/Recommends')
def Recommends():
    books = set()
    #get books in csv data
    with open('static/books.csv', encoding='utf-8', errors='ignore') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        line_count = 0
        for row in reader:
            if line_count == 0:
                line_count += 1
            else:
                books.add(row[1])

    return render_template('Recommends.html', books=books)
    
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
    print(session['currentDirectory'])
    targetDir = session['currentDirectory'] + "/"+request.form['targetFolder']
    print(targetDir)
    if len(os.listdir(targetDir)) == 0:
        os.rmdir(targetDir)
    else:    
        shutil.rmtree(targetDir)
    return ('', 204)

#method to make directory of user id(int) if does not exist.
def chckDir(id):
    if not os.path.exists("UserRepos/"+str(id)+"/Files/"):
        os.makedirs("UserRepos/"+str(id)+"/Files/")

#POST path to save Notes at specified directory
@app.route("/POSTSaveNotes", methods=["POST"])
def saveNoteOp():
    filename = request.form['fileName']
    targetDir = request.form['targetSaveLoc']
    text = request.form['text']

    #if no filename
    if(filename == False or filename == ''):
        filename = "Untitled"

    targetLoc = "UserRepos\\"+str(session['accountID'])+"\\Files"+targetDir+filename+".txt"
    f = open(targetLoc, "w+")
    f.write(text)
    f.close()

    return ('', 204)
        
#POST action to create new chat group
@app.route("/POSTNewChatGroup", methods=["POST"])
def createNewChat():
    
    chatName = request.form.get('chatName')         #String text    
    chatUsers = request.form.getlist('chatUsers')   #array of usernames allowed in chat
    chatPrivate = request.form.get('isPrivate')     #int value of 1(True) or 0(False)
    print(chatUsers)
    print(chatPrivate)
    #connect to DB
    conn = mysql.connect()
    cursor =conn.cursor()
    #Make DB chatroom
    try:
        cursor.execute("INSERT INTO chatrooms (RoomName,ID_RoomOwner,isPrivate) VALUES ('"+chatName+"',"+str(session['accountID'])+","+chatPrivate+")")
        conn.commit()
        #get this specific room's ID
        cursor.execute("SELECT ID_ChatRoom FROM chatrooms WHERE RoomName='"+chatName+"' AND ID_RoomOwner="+str(session['accountID'])+";")
        data = cursor.fetchone()
        roomID = data[0]
        #insert room members into DB
        for member in chatUsers:
            #find member ID
            cursor.execute("SELECT ID_User FROM users WHERE Handle='"+member+"';")
            memberID = cursor.fetchone()[0]
            #add participant users 
            #print("INSERT INTO roommembers (ID_ChatRoom,ID_Members) VALUES ("+str(roomID)+","+str(memberID)+");")
            cursor.execute("INSERT INTO roommembers (ID_ChatRoom,ID_Members) VALUES ("+str(roomID)+","+str(memberID)+");")
    except Exception as e:
        print(e)
        flash('Problem in creating chatroom: '+str(e))
    conn.commit()
    conn.close()
    return (redirect('/Chat'))

@app.route("/AccessChat",methods=["POST"])
def accessChat():
    # #Debugmode get
    # RType = 1
    # RId = 11
    # RName = "testchat"

    #get postdata
    if flask.request.method == 'POST':
        RType = request.form["roomType"]
        RId = request.form["targetRoomID"]
        RName = request.form["targetRoomName"]

    #connect to DB
    conn = mysql.connect()
    cursor =conn.cursor()
    #get owner of room
    cursor.execute("SELECT ID_RoomOwner, users.Handle FROM chatrooms INNER JOIN users on chatrooms.ID_RoomOwner=users.ID_User WHERE ID_Chatroom="+str(RId))
    data=cursor.fetchone()
    ROwner = tuple( [data[0],data[1]] )

    #get all members in chatroom
    cursor.execute("SELECT roommembers.ID_Members, users.Handle FROM `chatrooms` INNER JOIN `roommembers` ON chatrooms.ID_ChatRoom = roommembers.ID_ChatRoom INNER JOIN `users` ON roommembers.ID_Members = users.ID_User WHERE chatrooms.ID_ChatRoom="+str(RId))
    data= cursor.fetchall()
    RMembers = list()
    for entry in data:
        tempTuple = ( [entry[0],entry[1]] )
        RMembers.append( tempTuple )   #add (userID, userName)
    print("Members: "+str(RMembers))

    #get all users that are not member or owner
    #get all users first
    cursor.execute("SELECT ID_User, Handle FROM users")
    data = cursor.fetchall()
    ROtherUsers = list()
    #go through all users
    for entry in data:
        print("User ID: "+str(entry[0]))
        #check if user is owner
        if entry[0] != ROwner[0]:
            #check if user is a member
            if RMembers:
                aMember = False
                for member in RMembers:
                    if member[0] == entry[0]:
                        #if user is a member, flag
                        aMember = True     
                
                if(not aMember):
                    print("not a member")
                    tempTuple = ( [entry[0],entry[1]] )
                    ROtherUsers.append( tempTuple )
            else:   #if no members, add to list
                print("    No members, add")
                tempTuple = ( [entry[0],entry[1]] )
                ROtherUsers.append( tempTuple )
        else:   #if owner, continue
            print("    is owner, skip")
            continue

    #get all the texts in chatroom
    cursor.execute("SELECT chatmessages.ID_User,users.Handle,Content_Msg,Timestamp_Msg FROM chatmessages INNER JOIN users ON chatmessages.ID_User=users.ID_User WHERE ID_Chatroom="+str(RId)+" ORDER BY Timestamp_Msg ASC")
    data = cursor.fetchall()
    RTexts = data

    print("chatroom loaded")
    print("Other Users: "+str(ROtherUsers))
    return render_template("ChatRoom.html", RId=RId, RName=RName, ROwner=ROwner, RType=RType, RMembers=RMembers, RTexts=RTexts, currentUser=session["accountID"], ROtherUsers=ROtherUsers)

@app.route("/PostChatText", methods=["POST"])
def addChatText():
    # get post data
    senderID = session['accountID']
    tgtChtRm = request.form["tgtRoomId"]
    chatText = request.form["chatToSend"]
    
    #connect to DB
    conn = mysql.connect()
    cursor = conn.cursor()

    #put chat data into database
    try:
        cursor.execute("INSERT INTO chatmessages (ID_ChatRoom,ID_User,Content_Msg,Timestamp_Msg) VALUES ("+str(tgtChtRm)+","+str(senderID)+",'"+chatText+"',NOW());")
        conn.commit()
        conn.close()
    except Exception as e:
        print(e)
        flash('Problem in creating chatroom: '+str(e))
    print("Postchat done")
    return ('', 204)

@app.route("/POSTLeaveGroup", methods=["POST"])
def postLeaveChat():
    # get post data
    senderID = session['accountID']
    tgtChtRm = request.form["targetRoomID"]
    
    #connect to DB
    conn = mysql.connect()
    cursor = conn.cursor()

    #delete self from groupMembers 
    try:
        cursor.execute("DELETE FROM roommembers WHERE ID_Chatroom="+str(tgtChtRm)+" AND ID_Members="+str(senderID))
        conn.commit()
        conn.close()
        print("DELETE FROM roommembers WHERE ID_Chatroom="+str(tgtChtRm)+" AND ID_Members="+str(senderID))
    except Exception as e:
        print(e)
        flash('Problem in leaving chatroom: '+str(e))
    flash("Left group " + request.form['targetRoomName'])    
    return ('', 204)
@app.route("/POSTJoinGroup", methods=["POST"])
def postJoinChat():
    # get post data
    senderID = session['accountID']
    tgtChtRm = request.form["targetRoomID"]
    
    #connect to DB
    conn = mysql.connect()
    cursor = conn.cursor()

    #insert self from groupMembers 
    try:
        cursor.execute("INSERT INTO roommembers (ID_ChatRoom,ID_Members) VALUES ("+str(tgtChtRm)+","+str(senderID)+");")
        conn.commit()
        conn.close()
        print("INSERT INTO roommembers (ID_ChatRoom,ID_Members) VALUES ("+str(tgtChtRm)+","+str(senderID)+");")
    except Exception as e:
        print(e)
        flash('Problem in joining chatroom: '+str(e))
    flash("Joined group " + request.form['targetRoomName'])    
    return ('', 204)

@app.route("/OwnerAddMember", methods=["POST"])
def chatOwnerAddMember():
    tgtChtRm = request.form.get('targetRoomID')         
    newMembers = request.form.getlist('addMembers')
    #connect to DB
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        #insert users to groupMembers 
        for user in newMembers:
            cursor.execute("INSERT INTO roommembers (ID_ChatRoom,ID_Members) VALUES ("+str(tgtChtRm)+","+str(user)+");")
        conn.commit()
        conn.close()
    except Exception as e:
        print(e)
        flash('Problem in adding members: '+str(e)) 
    return ('', 204)


@app.route("/OwnerKickMember", methods=["POST"])
def chatOwnerRemMember():
    tgtChtRm = request.form.get('targetRoomID')         
    newMember = request.form.get('remMember')
    #connect to DB
    conn = mysql.connect()
    cursor = conn.cursor()
    print(newMember)
    try:
        #remove groupMember
        cursor.execute("DELETE FROM roommembers WHERE ID_Chatroom="+str(tgtChtRm)+" AND ID_Members="+str(newMember))
        conn.commit()
        conn.close()
    except Exception as e:
        print(e)
        flash('Problem in adding members: '+str(e)) 
    return ('', 204)

@app.route("/OwnerDeleteRoom", methods=["POST"])
def chatOwnerDelete():
    targetRoomID = request.form.get('targetRoomID')

    #connect to DB
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        #delete specific room -> should cascade delete rooms, roomMembers and chats
        cursor.execute("DELETE FROM chatrooms WHERE ID_Chatroom="+str(targetRoomID))
        conn.commit()
        conn.close()
    except Exception as e:
        print(e)
        flash('Problem in closing chatroom: '+str(e)) 
    return ('', 204)

@app.route("/findRecommends", methods=['POST'])
def findRecommends():
    book_name = request.form.get('baseBook')
    recBooks = BookRecommender(book_name)
    return render_template('BookRecommends.html', recBooks=recBooks)

####
## START camera capture functions
####
import base64 
import boto3
import creds
from botocore.exceptions import ClientError
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
    cursor.execute("SELECT handle FROM users WHERE ID_User="+str(session['accountID'])+";")
    data = cursor.fetchone()
    convert_and_save(accImageB64,data[0])
    flash('Image changed')
    return redirect(url_for('Profile', userData=data))

def convert_and_save(b64_string, name):
    #if userimages does not exist, create them.
    if not os.path.exists("static\\userimages\\"):
        os.makedirs("static\\userimages\\")
    filename="static\\userimages\\"+name+".jpg"
    imgdata = base64.b64decode(b64_string)
    with open(filename, 'wb') as f:
        f.write(imgdata)


def compare(source_image_name):
    rekognition_client = boto3.client('rekognition',
        aws_access_key_id=creds.rekognition['access_key_id'],
        aws_secret_access_key=creds.rekognition['secret_access_key'],
        region_name=creds.rekognition['region'],
    )
    
    FOLDER_NAME = 'static/userimages'
    source_image_path = '%s/%s' % (FOLDER_NAME, source_image_name)
    target_image_path = '%s/%s' % (FOLDER_NAME, "temp.jpg")

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
        
        
        
        
        
        
        
        
        
        
        
