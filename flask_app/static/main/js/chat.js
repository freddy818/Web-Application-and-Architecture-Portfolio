var socket;

/** Given from the starter code, i just moved it into a js file */
$(document).ready(function(){
    
    socket = io.connect('https://' + document.domain + ':' + location.port + '/chat');
    socket.on('connect', function() {
        socket.emit('joined', {});
    });
    
    socket.on('status', function(data) {     
        let tag  = document.createElement("p");
        let text = document.createTextNode(data.msg);
        let element = document.getElementById("chat");
        tag.appendChild(text);
        tag.style.cssText = data.style;
        element.appendChild(tag);
        $('#chat').scrollTop($('#chat')[0].scrollHeight);

    });        
});

/** when enter key is pressed */
const msg = document.getElementById("msg");
msg.addEventListener("keydown", function(send_msg){
    if (send_msg.key === 'Enter')
    {
        if (send_msg.target.value !== "")
        {
            /** when the msg isnt empty, send the msg to the chat room using socket.emit */
            socket = io.connect('https://' + document.domain + ':' + location.port + '/chat');
            socket.emit('send', send_msg.target.value);
            send_msg.target.value = "";

        }
    }
});

const leavebutton = document.getElementById('leaveChat');
leavebutton.addEventListener('click', function(event){
    /** call emit and then boot you back to the home page when the leave button is clicked */
    socket.emit('leave', {});
    window.location.href = "/home";

});

    

