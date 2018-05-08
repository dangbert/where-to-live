<?php
    /*
     * This file takes a GET request with param geo_id 
     * and returns the data from datausa.io as json
     */
    // before running this, make sure you create a database called "code_fury" and a user "code_fury"
    $host = "localhost";
    $dbname = "code_fury";
    $username = "code_fury";
    $password = "devpassword";

    try {
        $db = new PDO('mysql:host=' . $host . ';dbname=' . $dbname, $username, $password);
        $db->setAttribute( PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION ); // Error Handling
    }
    catch(PDOException $e) {
        echo "ERROR<br>";
        echo $e->getMessage();
    }

    $sql = "SELECT id, geo_id, state_id FROM counties order by id asc;";
    $geoID = $_GET['geo_id'];
    // query datausa api for attributes about this county
    $url = "https://api.datausa.io/api/?show=geo&sumlevel=county&geo=" . $geoID . "&year=latest&required=";
    $public_trans_vals = getRequest($url . "transport_publictrans,workers")['data'][0];
    if (empty($public_trans_vals)) {
        $public_trans = NULL;
    } else {
        $public_trans = floatval($public_trans_vals[2]) / floatval($public_trans_vals[3]);
    }

    $public_schools = getRequest($url . "high_school_graduation")['data'][0][2];
    $commute_time = getRequest($url . "mean_commute_minutes")['data'][0][2];
    $crime_rates = getRequest($url . "violent_crime")['data'][0][2];
    $healthcare = getRequest($url . "primary_care_physicians")['data'][0][2];

    $result = array(
        "public_trans" => $public_trans,
        "public_schools" => $public_schools,
        "commute_time" => $commute_time,
        "crime_rates" => $crime_rates,
        "healthcare " => $healthcare 
    );

    echo json_encode($result);


    // do a GET request on $url and decode the result from json into an array
    // return: array
    function getRequest($url) {
        // url to GET info for this table
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
        $output = curl_exec($ch);
        if (curl_errno($ch)) {                  // Check if any error occurred
            echo 'Curl error: ' . curl_error($ch);
        }
        curl_close($ch);                        // close curl resource to free up system resources
        $res = json_decode($output, true);      // json to array
        return $res;
    }
?>
