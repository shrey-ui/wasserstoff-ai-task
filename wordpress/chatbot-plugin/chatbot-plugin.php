<?php
/*
Plugin Name: Chatbot Integration
Description: Integrates a chatbot with the WordPress site and sends queries to a Flask API.
Version: 1.0
Author: Your Name
*/

// Enqueue the chatbot JavaScript
function enqueue_chatbot_script() {
    wp_enqueue_script('jquery');
    wp_enqueue_script('chatbot-script', plugin_dir_url(__FILE__) . 'chatbot.js', array('jquery'), null, true);
    wp_localize_script('chatbot-script', 'chatbot_ajax', array('ajax_url' => admin_url('admin-ajax.php')));
}

// Add chatbot HTML to the footer
function add_chatbot_html() {
    ?>
    
    <div id="chatbot">
        <div id="chatbot-header">Chatbot</div>
        <div id="chatbot-messages"></div>
        <input type="text" id="chatbot-input" placeholder="Type your query...">
        <button id="chatbot-send">Send</button>
    </div>
    <style>
        #chatbot {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 400px;
        height: 600px;
        background-color: #000;
        color: #fff;
        border: 1px solid #fff;
        border-radius: 5px;
        box-shadow: 0 0 10px rgba(255, 255, 255, 0.1);
        z-index: 9999;
    }

    #chatbot-header {
        background-color: #333;
        padding: 10px;
        text-align: center;
        cursor: pointer;
    }

    #chatbot-messages {
        max-height: 200px;
        overflow-y: auto;
        padding: 10px;
    }

    #chatbot-input {
        width: calc(100% - 20px);
        margin: 10px;
        padding: 10px;
        border: 1px solid #fff;
        border-radius: 5px;
        background-color: #333;
        color: #fff;
    }

    #chatbot-send {
        width: calc(100% - 20px);
        margin: 10px;
        padding: 10px;
        background-color: #333;
        color: #fff;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }

    </style>
    <script>
        document.addEventListener("DOMContentLoaded", function() {
            console.log("Chatbot script loaded");
            document.getElementById("chatbot-header").onclick = function() {
                var chatbot = document.getElementById("chatbot");
                if (chatbot.style.display === "none" || chatbot.style.display === "") {
                    chatbot.style.display = "block";
                } else {
                    chatbot.style.display = "none";
                }
            };
        });
    </script>
    <?php
}
add_action('wp_enqueue_scripts', 'enqueue_chatbot_script');
add_action('wp_footer', 'add_chatbot_html', 1000);

// Handle the chatbot AJAX request
function handle_chatbot_query() {
    header("Access-Control-Allow-Origin: *"); // Allow CORS from any origin
    header("Access-Control-Allow-Methods: POST, GET, OPTIONS");
    header("Access-Control-Allow-Headers: Content-Type, Authorization");

    if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
        // Handle preflight request
        exit(0);
    }

    $query = sanitize_text_field($_POST['query']);
    $site_url = get_site_url();

    $response = wp_remote_post('http://127.0.0.1:5001/chatbot', array(
        'method'    => 'POST',
        'body'      => json_encode(array('query' => $query, 'wordpress_link' => get_site_url())),
        'headers'   => array('Content-Type' => 'application/json')
    ));

    

    

    // if (is_wp_error($response)) {
    //     wp_send_json_error('Error communicating with Flask API');
    // } else {
    $body = wp_remote_retrieve_body($response);
    wp_send_json_success($body);
    // }
}
add_action('wp_ajax_chatbot_query', 'handle_chatbot_query');
add_action('wp_ajax_nopriv_chatbot_query', 'handle_chatbot_query');




