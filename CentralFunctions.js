function populateData(){
    //get user's file array and data from DB

    //put item list into table rows
}
function loadProfile(){
    //get user's info and display
}

//Switch Iframe source displays
function switchFrameToProfile(){
    var frame = document.getElementById("OperatingWindow")
    frame.src = "Profile.html"
}
function switchFrameToList(){
    var frame = document.getElementById("OperatingWindow")
    frame.src = "ItemTables.html"
}
function switchFrameToChat(){
    var frame = document.getElementById("OperatingWindow")
    frame.src = "Chat.html"
}
function switchFrameToNotes(){
    var frame = document.getElementById("OperatingWindow")
    frame.src = "Notes.html"
}
function switchFrameToReminders(){
    var frame = document.getElementById("OperatingWindow")
    frame.src = "Reminders.html"
}

//simple goto links
function gotoZoom(){
    window.location.href= "https://zoom.us/signin"
}
function gotoBB(){
    window.location.href="https://douglascollege.blackboard.com/webapps/login/"
}
function gotoTranslink(){
    window.location.href="https://upassbc.translink.ca/"
}
function gotoMyAccount(){
    window.location.href="https://banappssb2.douglascollege.ca/ssomanager/c/SSB"
}

//log out function
function logOut(){
    //remove sign in info from local machine
    window.location.href="index.html"
}