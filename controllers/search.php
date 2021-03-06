<?php
    // this file will handle a post request with search parameters
    // and return the data needed to display the results (likely as JSON)

    // connect to database
    $host = "localhost";
    $dbname = "code_fury";
    $username = "code_fury";
    $password = "devpassword";
    try {
        $db = new PDO('mysql:host=' . $host . ';dbname=' . $dbname, $username, $password);
        $db->setAttribute( PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION ); // Error Handling
    }
    catch(PDOException $e) {
        echo "ERROR connecting to database<br>";
        echo $e->getMessage();
    }


    /* percentiles:
    {'public_schools': {'33': 0.84, '66': 0.907},
    'public_trans': {'33': 0.0018959374599999991, '66': 0.005931874919999998},
    'crime_rates': {'33': 142.4358816, '66': 275.06529279999995},
    'healthcare': {'33': 40.0, '66': 64.0},
    'avg_temp': {'33': 506.0, '66': 581.0, '50': 544.5},
    'precipitation': {'33': 3408.4737999999998, '66': 4620.48952},
    'snow': {'33': 51.98951999999986, '66': 266.374}}
    */
    // recreation and commute are excluded from this array
    $ranges = array(
        "schools" => array(
            0 => 0.84,                          // low:     values <= [0]        (33rd percentile)
            1 => 0.907                          // medium:  [0] < values < [1]   (66th percentile)
                                                // high:    values >= [1]
        ),
        "transportation" => array(
            0 => 0.01,                          // low:     values <= [0]        (manually set)
            1 => 0.07                           // medium:  [0] < values < [1]   (manually set)
                                                // high:    values >= [1]
        ),
        "crime" => array(
            0 => 142.4358816,                   // low:     values <= [0]        (33rd percentile)
            1 => 275.06529279999995             // average: [0] < values < [1]   (66th percentile)
        ),
        "temperature" => array(
            0 => 544.5,                         // colder:  values <= [0]        (50th percentile)
                                                // hotter:  values > [0]
        ),
        "precipitation" => array(
            0 => 3408.4737999999998,            // low:     values <= [0]        (33rd percentile)
            1 => 4620.48952                     // medium:  [0] < values < [1]   (66th percentile)
                                                // high:    values >= [1]
        ),
        "snowfall" => array(
            0 => 51.98951999999986,             // low:     values <= [0]        (33rd percentile)
            1 => 266.374                        // medium:  [0] < values < [1]   (66th percentile)
                                                // high:    values >= [1]
        ),
        "healthcare" => array(
            0 => 40.0,                          // average: [0] < values < [1]    (33rd percentile)
            1 => 64.0,                          // high:    values >= [1]         (66th percentile)
        )
    );

    // for now send a short string back as a test
    $data = json_decode(file_get_contents('php://input'), true);
    $first = True;                              // we have used any of the varibles yet
    //print_r($data);

    // TODO: add "or $col is NULL" to everything

    // build the condition portion of the sql query string
    $sql = "";
    // SCHOOLS (0: low, 1: medium, 2:high) (inclusive)
    if ($data["schools"]["enabled"] === TRUE) {
        $sql .= prepareCondition($data["schools"]["value"], $ranges, "schools", "public_schools", true);
        $first = False;
    }
    // TRANSPORTATION (0: low, 1: medium, 2: average) (inclusive)
    if ($data["transportation"]["enabled"] === TRUE) {
        $sql .= ($first ? "" : " and ");
        $sql .= prepareCondition($data["transportation"]["value"], $ranges, "transportation", "public_trans", true);
        $first = False;
    }
    // CRIME (0: low, 1: average) (inclusive)
    if ($data["crime"]["enabled"] === TRUE) {
        // average should include low as well
        $sql .= ($first ? "" : " and ");
        $sql .= " (crime_rates < " . $ranges["crime"][$data["crime"]["value"]] . ")";
        $first = False;
    }
    // CLIMATE
    if ($data["climate"]["enabled"] === TRUE) {
        // TEMPERATURE (0: no preference, 1: hotter, 2: colder)
        if ($data["climate"]["value"]["temperature"] !== 0) {
            $symbol = ($data["climate"]["value"]["temperature"] === 2 ? "<=" : ">");
            $sql .= ($first ? "" : " and ");
            $sql .= " (avg_temp $symbol " . $ranges["temperature"][0] . ")";
            $first = False;
        }
        // PRECIPITATION (0: low, 1: medium, 2: high)
        $sql .= ($first ? "" : " and ");
        $sql .= prepareCondition($data["climate"]["value"]["precipitation"], $ranges, "precipitation", "precipitation", false);
        $first = False;

        // SNOWFALL (0: low, 1: medium, 2: high)
        $sql .= ($first ? "" : " and ");
        $sql .= prepareCondition($data["climate"]["value"]["snowfall"], $ranges, "snowfall", "snow", false);
        $first = False;
    }
    // HEALTHCARE (0: average, 1: high) (inclusive)
    if ($data["healthcare"]["enabled"] === TRUE) {
        // high should include average as well
        $sql .= ($first ? "" : " and ");
        $sql .= " (healthcare > " . $ranges["healthcare"][$data["healthcare"]["value"]] . ")";
        $first = False;
    }
    // COMMUTE (value: int 0-60) (ensures commute is <= value)
    if ($data["commute"]["enabled"] === TRUE) {
        $sql .= ($first ? "" : " and ");
        $sql .= " (commute_time <= " . $data["commute"]["value"] . ")";
        $first = False;
    }
    // RECREATION:
    if ($data["recreation"]["enabled"] === TRUE) {
        $activities = array("biking", "climbing", "camping", "hiking", "hunting", "wilderness", "swimming");
        $str = "";
        foreach($activities as &$value) {
            if ($data["recreation"]["value"]["has_$value"] == TRUE) {
                $str .= "($value >= 1) or ";
            }
        }
        if ($str != "") {  // make sure at least one activity was enabled
            $str = ($first ? " (" : " and (") . $str;
            $sql .= substr($str, 0, -3) . ")";  // remove last 'or'
            $first = False;
        }
    }


    if ($first) { // no results
        echo json_encode(array());
    }
    else {
        // this part of the query combines the tables (counties, states, recareas) into a table of rows of counties with the added fields state (state name) and fields for the number of recareas in the county that provide each rec activity
        $combineQuery = "
            (SELECT counties.*, states.name as state from counties join states on counties.state_id = states.id) t1
            LEFT JOIN
            (select county_id, sum(has_biking) as biking, sum(has_climbing) as climbing, sum(has_camping) as camping, sum(has_hiking) as hiking, sum(has_hunting) as hunting, sum(has_wilderness) as wilderness, sum(has_swimming) as swimming from recareas group by county_id) t2
            ON t1.id = t2.county_id
            ";

        // final query string, apply the conditions to the combined table and just get the state and county name of the results
        $sql = "SELECT state, name as county, public_schools, public_trans, commute_time, crime_rates, healthcare, precipitation, avg_temp, snow, biking, climbing, camping, hiking, hunting, wilderness, swimming, lat, lng FROM ($combineQuery) WHERE $sql;";
        //echo $sql . "\n\n";

        // do the query and return the results as JSON
        $results = $db->query($sql)->fetchAll();
        $arr = array();
        foreach($results as &$row) {
            array_push($arr, array("county" => $row["county"], "state" => $row["state"], "public_schools" => $row["public_schools"], "public_trans" => $row["public_trans"], "commute_time" => $row["commute_time"], "crime_rates" => $row["crime_rates"], "healthcare" => $row["healthcare"], "precipitation" => $row["precipitation"], "avg_temp" => $row["avg_temp"], "snow" => $row["snow"], "biking" => $row["biking"], "climbing" => $row["climbing"], "camping" => $row["camping"], "hiking" => $row["hiking"], "hunting" => $row["hunting"], "wilderness" => $row["wilderness"], "swimming" => $row["swimming"], "lat" => $row["lat"], "lng" => $row["lng"]));
            //print_r($row);
        }
        echo json_encode($arr);
    }

    // create portion of search string for given column
    // value:  int value representing the search preference
    // ranges: array of predefined ranges for the possible values
    // label:  name of key in ranges array
    // col:    name of column in counties table
    // inclusive: bool whether or not the search should be inclusive
    //            (e.g. medium transportation would include high as well)
    // returns a string
    function prepareCondition($value, $ranges, $label, $col, $inclusive) {
        $str = "";
        //$value = $data[$label]["value"];
        if ($inclusive) {
            if ($value === 0) {
                $str .= " ($col >= 0)"; // all results (where not null)
            }
            if ($value === 1) {
                $str .= " ($col > " . $ranges[$label][0] . ")";
            }
            if ($value === 2) {
                $str .= " ($col >= " . $ranges[$label][1] . ")";
            }
        }
        else {
            $str = "";
            //$value = $data[$label]["value"];
            if ($value === 0) {
                $str .= " ($col <= " . $ranges[$label][0] . ")";
            }
            if ($value === 1) {
                $str .= " ($col > " . $ranges[$label][0] . " and $col < " . $ranges["$label"][1] . ")";
            }
            if ($value === 2) {
                $str .= " ($col >= " . $ranges[$label][1] . ")";
            }
        }

        return $str;
    }
?>
