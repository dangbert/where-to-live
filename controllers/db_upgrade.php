<?php
    // before running this, make sure you create a database called "code_fury" and a user "code_fury"
    $host = "localhost";
    $dbname = "code_fury";
    $username = "code_fury";
    $password = "devpassword";

    echo "attempting to connect to mysql database...<br>";
    try {
        $db = new PDO('mysql:host=' . $host . ';dbname=' . $dbname, $username, $password);
        $db->setAttribute( PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION ); // Error Handling
        echo "connection success!<br>";
    }
    catch(PDOException $e) {
        echo "ERROR<br>";
        echo $e->getMessage();
    }

    $latest_version = 2; // update this everytime a new version is added to this script
    $version = getDB_version($db);
    echo "Current DB version is " . $version . "<br>";
    if ($version == -1) {
        echo "ERROR: some table exist but not all. Delete tables and run again.";
        die();
    }
    if ($version == $latest_version) {
        echo "Database is already at the latest version.<br>";
        die();
    }
    if ($version == 0) {
        // create tables
        try {
            // table for keeping track of the database version
            $sql = "CREATE table db_version(
            id INT( 11 ) AUTO_INCREMENT PRIMARY KEY,
            version INT( 11 ) NOT NULL);";
            $db->exec($sql);

            // create 'states' table
            $sql = "CREATE table states(
            id INT( 11 ) AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR( 30 ) NOT NULL,
            geo_id VARCHAR( 20 ) NOT NULL);";
            $db->exec($sql);

            // create 'counties' table
            $sql = "CREATE table counties(
            id INT( 11 ) AUTO_INCREMENT PRIMARY KEY,
            state_id INT( 11 ) NOT NULL,
            name VARCHAR( 50 ) NOT NULL,
            geo_id VARCHAR( 20 ) NOT NULL);";
            $db->exec($sql);

            // index on state_id to make it faster
            // TODO: consider also indexing on one or two of the data columns to make search even faster
            $sql = "CREATE INDEX ix_state_id ON counties(state_id);";
            $db->exec($sql);
        }
        catch(PDOException $e) {
            echo "Error creating table<br>";
        }

        // get list of states and store in the 'states' table
        $url = "https://api.datausa.io/attrs/geo/01000US/children/";
        $states = getRequest($url)["data"];
        // iterate over each state (also includes "Puerto Rico" and "District of Columbia")
        // TODO: consider omitting Puerto Rico
        foreach ($states as &$state) {
            $name = $state[1];     // state name
            $geo_id = $state[0];   // geo_id

            // insert row into 'states' table
            $statement = $db->prepare("INSERT INTO states(name, geo_id)
            VALUES(:name, :geo_id)");
            $statement->execute(array(
                "name" => $name,
                "geo_id" => $geo_id
            ));

            // iterate over each county in this state
            $state_id = $db->lastInsertID();       // ID of the current state
            $url = "https://api.datausa.io/attrs/geo/" . $geo_id . "/children/";
            $counties = getRequest($url)["data"];
            foreach ($counties as &$county) {
                // insert row into 'counties' table
                $statement = $db->prepare("INSERT INTO counties(state_id, name, geo_id)
                VALUES(:state_id, :name, :geo_id)");
                $statement->execute(array(
                    "state_id" => $state_id,
                    "name" => explode(",", $county[1])[0], // some are like "Howard County, MD"
                    "geo_id" => $county[0]
                ));
            }
        }
        setDB_version($db, 1);
    }

    if (getDB_version($db) == 1) {
        // add columns to 'counties' table
        $sql = "ALTER table counties
            ADD public_schools DECIMAL(12,6) NULL,
            ADD public_trans DECIMAL(12,6) NULL,
            ADD commute_time DECIMAL(12,6) NULL,
            ADD crime_rates DECIMAL(12,6) NULL,
            ADD healthcare INT(11) NULL;";
        $db->exec($sql);

        $sql = "SELECT id, geo_id, state_id FROM counties;";
        $results = $db->query($sql)->fetchAll();
        foreach ($results as &$res) {
            // query datausa api for attributes about this county
            $url = "https://api.datausa.io/api/?show=geo&sumlevel=county&geo=" . $res['geo_id'] . "&year=latest&required=";
            $public_trans_vals = getRequest($url . "transport_publictrans,workers")['data'][0];
            if (empty($public_trans_vals)) {
                echo $res['id'] . "flag1<br>";
                $public_trans = NULL;
            } else {
                $public_trans = floatval($public_trans_vals[2]) / floatval($public_trans_vals[3]);
            }

            $public_schools = getRequest($url . "high_school_graduation")['data'][0][2];
            $commute_time = getRequest($url . "mean_commute_minutes")['data'][0][2];
            $crime_rates = getRequest($url . "violent_crime")['data'][0][2];
            $healthcare = getRequest($url . "primary_care_physicians")['data'][0][2];

            // now store the attributes in row in table
            $statement = $db->prepare("UPDATE counties SET
            public_schools = :public_schools, public_trans = :public_trans, commute_time = :commute_time, crime_rates = :crime_rates, healthcare = :healthcare
            WHERE id = :county_id;");
            // leave attributes as NULL if the data doesn't exist
            $statement->execute(array(
                "public_schools" => (empty($public_schools) && $public_schools !== 0 ? NULL : floatval($public_schools)),
                "public_trans" => ($public_trans === NULL ? NULL : floatval($public_trans)),
                "commute_time" => (empty($commute_time) && $commute_time !== 0 ? NULL : floatval($commute_time)),
                "crime_rates" => (empty($crime_rates) && $crime_rates !== 0 ? NULL : floatval($crime_rates)),
                "healthcare" => (empty($healthcare) && $healthcare !== 0 ? NULL : intval($healthcare)),
                "county_id" => $res['id']
            ));
        }

        setDB_version($db, 2);
    }



    // HELPER FUNCTIONS:

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

    // return current database version
    function getDB_version($db) {
        $tmp = $db->prepare("show tables like 'states';");
        $tmp->execute();
        $tmp2 = $db->prepare("show tables like 'counties';");
        $tmp2->execute();
        $tmp3 = $db->prepare("show tables like 'db_version';");
        $tmp3->execute();
        // no tables exist
        if ($tmp->rowCount() == 0 && $tmp2->rowCount() == 0 && $tmp3->rowCount() == 0) {
            return 0;
        }
        // all tables exist
        elseif ($tmp->rowCount() == 1 && $tmp2->rowCount() == 1 && $tmp3->rowCount() == 1) {
            // get current db version
            $sql = "SELECT version FROM db_version order by id desc limit 1";
            $res = $db->query($sql)->fetch();
            return $res[0];
        }
        // only some tables already exist:
        else {
            return -1;
        }
    }

    // UPDATE database version to given version (string)
    function setDB_version($db, $version) {
        $statement = $db->prepare("INSERT INTO db_version(version)
        VALUES(:version)");
        $statement->execute(array(
            "version" => $version
        ));
        echo "Updated database to version " . $version . "<br>";
    }
?>
