<?php
/*
Plugin Name: Vector DB Updater
Description: Updates the vector database whenever a new post is created.
Version: 1.0
Author: Shreyans Murkute for Wasserstoff
*/

function send_post_data_to_api($post_ID, $post, $update) {
    if ($update) {
        error_log('Post updated, not a new post');
        return; // Only proceed if this is a new post
    }

    $post_data = array(
        'ID' => $post_ID,
        'post_title' => $post->post_title,
        'post_content' => $post->post_content,
        'site_url' => get_site_url()
    );

    $response = wp_remote_post('http://127.0.0.1:5001/update-vector-db', array(
        'method'    => 'POST',
        'body'      => json_encode($post_data),
        'headers'   => array('Content-Type' => 'application/json')
    ));

    if (is_wp_error($response)) {
        error_log('Error sending post data to API: ' . $response->get_error_message());
    }else{
        error_log('Post data sent to API. response -> ' . print_r($response, true));
    }
}

add_action('wp_insert_post', 'send_post_data_to_api', 10, 3);