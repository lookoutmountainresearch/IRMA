<?php
    $result = filter_input ( INPUT_GET , 'image' );
    if (isset($result) && !empty($result)) {
        echo '<img src="images\LookoutMountainResearch_Logo.png">';
    }
?>
