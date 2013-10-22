$(function() {
    // expected url: http://location:5000/chat/{chatroom}
    var url = document.URL,
        chatroom = "",
        // expected result: chat/{chatroom}
        url = url.substr(url.indexOf('chat'));
        if(url.indexOf('/')) {
            chatroom = url.split('/')[1];
        }

        sendMessage = function() {
            var message = textarea.val();
            $.ajax({
                url: '/chat/' + chatroom + '/message',
                type: "POST",
                data: JSON.stringify({
                    "message": message
                }),
                processData: false,
                success: function(posted) {
                    alert(posted);
                },
                contentType: "application/json",
                dataType: "application/json"
            });
        };
    var textarea = $('textarea');
    $('input[type="button"]').click(sendMessage);
});
