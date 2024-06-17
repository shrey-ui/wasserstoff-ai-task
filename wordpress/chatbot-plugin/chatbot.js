jQuery(document).ready(function($) {
    console.log("Chatbot JavaScript loaded");

    $('#chatbot-send').on('click', function() {
        var query = $('#chatbot-input').val();
        if (query.trim() === '') {
            $('#chatbot-messages').append('<div>Bot: Please enter a query.</div>');
            return;
        }

        $('#chatbot-messages').append('<div>User: ' + query + '</div>');
        $('#chatbot-input').val('');

        $.ajax({
            url: chatbot_ajax.ajax_url,
            crossDomain:true,
            cache:false,
            method: 'POST',
            data: {
                action: 'chatbot_query',
                query: query
            },
            success: function(response) {
                if (response.success) {
                    console.log(JSON.parse(response.data)['chatbot_response'])
                    $('#chatbot-messages').append('<div>Bot: ' + JSON.parse(response.data)["chatbot_response"] + '</div>');
                } else {
                    var errorMessage = 'Error occurred while fetching response.';
                    $('#chatbot-messages').append('<div>Bot: ' + errorMessage + '</div>');
                    console.error(errorMessage, response.data);
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                var errorMessage = 'Error occurred while sending request: ' + textStatus + ' - ' + errorThrown;
                $('#chatbot-messages').append('<div>Bot: ' + errorMessage + '</div>');
                console.error(errorMessage, jqXHR);
            }
        });
    });
});
