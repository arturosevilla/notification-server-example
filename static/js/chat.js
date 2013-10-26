$(function() {
    // expected url: http://location:5000/chat/{chatroom}
    var url = document.URL,
        chatroom = "",
        textarea = $('textarea'),
        messages = $('.messages'),
        sendMessage = function() {
            var message = textarea.val();
            $.ajax({
                url: '/chat/' + chatroom + '/message',
                type: "POST",
                data: JSON.stringify({
                    "message": message
                }),
                processData: false,
                complete: function(posted) {
                    scrollToBottom();
                },
                contentType: "application/json",
                dataType: "application/json"
            });
        },
        renderMessage = function(message) {
            console.log('rendering message');
            console.log(message);
            scrollToBottom();
        },
        scrollToBottom  = function() {
            messages[0].scrollTop = messages[0].scrollHeight;
        }

    // expected result: chat/{chatroom}
    url = url.substr(url.indexOf('chat'));

    if(url.indexOf('/')) {
        chatroom = url.split('/')[1];
    }

    $('input[type="button"]').click(sendMessage);
    
    // setup socketIO listener
    var messagesSocket =  io.connect('http://localhost:5886');
    messagesSocket.on('notifexample', function(data) {
        console.log('notification received');
        console.log('data');
        renderMessage(data);
    });
});
