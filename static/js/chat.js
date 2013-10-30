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
                    renderMessage({
                        message: message,
                        author: userName,
                        createdOn: moment().format('YYYY-MM-DD hh:mm:ss')
                    });
                    scrollToBottom();
                },
                contentType: "application/json",
                dataType: "application/json"
            });
        },
        renderMessage = function(message) {
            console.log('rendering message');
            var messageItem = $('<div class="message">'
                    + '<p><span class="author"></span><span class="text"></span></p>'
                    + '<div class="createdon"></div>'
                + '</div>');
            messageItem.find('.author')[0].innerText = message.author;
            messageItem.find('.author')[0].textContent = message.author;
            messageItem.find('.text')[0].innerText = message.message;
            messageItem.find('.text')[0].textContent = message.message;
            messageItem.find('.createdon')[0].innerText = message.createdOn;
            messageItem.find('.createdon')[0].textContent = message.createdOn;
            messages.append(messageItem);
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
        renderMessage(data.notification);
    });
});
