<?php
    // before running this, make sure you create a database called "code_fury" and a user "code_fury"
    $host = "localhost";
    $dbname = "code_fury";
    $username = "code_fury";
    $password = "devpassword";

    echo "attempting to connect to mysql database...<br>";
    try {
        $db = new PDO('mysql:host=' . $host . ';dbname=' . $dbname, $username, $password);
        $db->setAttribute( PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION ); //Error Handling
        echo "connection success!<br>";
    }
    catch(PDOException $e) {
        echo "ERROR<br>";
        echo $e->getMessage();
    }

    // quit if the states table already exists
    $tmp = $db->prepare("show tables like 'states';");
    $tmp->execute();
    if ($tmp->rowCount() != 0) {
        echo "ERROR: table 'states' already exists<br>";
        die();
    }

    // create table
    try {
        $sql = "CREATE table states(
        id INT( 11 ) AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR( 30 ) NOT NULL,
        geo_id VARCHAR( 20 ) NOT NULL);";

        $db->exec($sql);
    }
    catch(PDOException $e) {
        echo "Error creating table<br>";
    }

    // get list of states and store in the 'states' table
    $url = "https://api.datausa.io/attrs/geo/01000US/children/";
    $res = getRequest($url)["data"];
    // iterate over each state (also includes "Puerto Rico" and "District of Columbia")
    foreach ($res as &$val) {
        $name = $val[1];     // state name
        $geo_id = $val[0];   // geo_id

        // insert row into table
        $statement = $db->prepare("INSERT INTO states(name, geo_id)
        VALUES(:name, :geo_id)");
        $statement->execute(array(
            "name" => $name,
            "geo_id" => $geo_id
        ));
    }



    // go a GET request on $url and decode the result from json into an array
    // return: array
    function getRequest($url) {
        echo "in getRequest";
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
