<?php
    $accName = $_POST['accountName'];
    $accPass = $_POST['accountPass'];

    $con = mysqli_connect('localhost', 'root', '','notespack_db');

    $query = "SELECT * FROM users WHERE Handle='".$accName."' AND Password='".$accPass."'";
    $rs = mysqli_query($con, $query);
	$flag = false;
	foreach($rs as $row) {
		$flag = true;
	}
    if($flag){
        header("Location: Main.html");
    }
    else{
        header("Location: index.html?message=NotFound");   
    }
?>