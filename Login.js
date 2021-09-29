function login(){
    //Validate login
    let loginName = document.forms["credentials"]["accountName"].value
    let loginPass = document.forms["credentials"]["accountPass"].value
    alert("Login Name:"+loginName+"\nLogin Pass:"+loginPass)
    //go to main page
    window.location.href="Main.html"
    return false
}

function addNewUser(){

}