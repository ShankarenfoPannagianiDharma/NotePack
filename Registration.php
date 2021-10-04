<?php
    //registration puts data into DB then redirects into main if successful. Return to registration if fail.

    $accName = $_POST['AccountName'];
    $accPass = $_POST['Password'];
    $accMail = $_POST['EMail'];

    //VALIDATION
    $pwd_expression = "/^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-])/";
    $letters = "/^[A-Za-z]+$/";
    $filter = "/^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/";

    if($accName=='') {
        header("Location: Registration.html?message=emptyAccN");
    }
    else if(!preg_match($letters,$accName)) {
        header("Location: Registration.html?message=AccNOnlyAlph");
    }
    else if($accMail==''){
        header("Location: Registration.html?message=emptyAccM");
    }
    else if (!preg_match($filter,$accMail)) {
        header("Location: Registration.html?message=accMInv");
    }
    else if($accPass){
        header("Location: Registration.html?message=emptyPss");
    }
    /* password restrictions not necessary 
    else if(!preg_match($pwd_expression,$accPass)){
        header("Location: Registration.html?message=PssInv");
    }
    else if(strlen($accPass) < 6){
        header("Location: Registration.html?message=PssShrt");
    }
    else if(strlen($accPass) > 12){
        header("Location: Registration.html?message=PssLong");
    }
    */

    $con = mysqli_connect('localhost', 'root', '','notespack_db');

    //check if a duplicate entry exists
    $query = "SELECT * FROM users WHERE UPPER(Handle) = UPPER('$accName')";
    $rs = mysqli_query($con, $query);
	$flag = false;
	foreach($rs as $row) {
		$flag = true;
	}
    if($flag) { //if duplicate is found 
        header("Location: Registration.html?message=dupl"); 
    }
    else {
        $query = "INSERT INTO users (Handle, Password, Email) VALUES ('$accName','$accPass','$accMail')";
        $rs = mysqli_query($con, $query);
        header("Location: Main.html");
    }

    $con.close();
?>