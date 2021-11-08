function onLoad(){
    document.getElementById("CreateNewChat").onClick = function() {
        alert("NEWCHAT");
        $(".MainScreen").removeClass("active");
        $(".CreateNewChatDialog").addClass("active");
        alert("HEY");
    }
    
    document.getElementById("CancelNewChatDialog").onClick = function(){
        $(".MainScreen").addClass("active");
        $(".CreateNewChatDialog").removeClass("active");
    }
    
    function SendToChat(){
        chatText = document.getElementById("chatToSend").value();
    
        //make POST
        $.post(
            "/POSTSendChat",
            {
                chatMSG = chatText
            }
        );
    }
    
    
}