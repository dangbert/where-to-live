<!DOCTYPE html>
<html>
    <head>
        <title>Code Fury</title>
        <meta charset="utf-8">

        <!-- our css -->
        <link href="static/style.css" rel="stylesheet">
        <!-- boostrap css -->
        <link href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" rel="stylesheet">
    </head>

    <body>
        <?php echo "<p>Hello world<p>"; ?>
        <button type="button" id="search-button" class="btn btn-primary">Search</button>

        <!-- nav bar which will actually have search paramaters -->
        <div id="mySidenav" class="sidenav">
            <a href="javascript:void(0)" class="closebtn" onclick="closeNav()">&times;</a>
            <h3>Search Options:</h3>
            <div class="search-option">
                <!-- Rounded switch -->
                <label class="switch">
                    <input type="checkbox" checked>
                    <span class="slider round"></span>
                </label>
                Public Schools
            </div>
            <div class="search-option">
                <!-- Rounded switch -->
                <label class="switch">
                    <input type="checkbox" checked>
                    <span class="slider round"></span>
                </label>
                Public Transportation
            </div>

        </div>

        <!-- hamburger button to open navbar-->
        <span style="font-size:30px;cursor:pointer" onclick="openNav()">&#9776; Search Options</span>

        <!--where the map will be rendered-->  
        <center><div id="map"></div></center>


        <!-- scripts to include: -->
        <!-- jquery -->
        <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.3.1/jquery.js"></script>
        <!-- bootstrap -->
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js"></script>
        <!-- our javascript -->
        <script src="static/script.js"></script>
        <!-- import google maps api (using my api key) -->
        <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyAIWdpUpiQnAIxMvVywRq7aVMDqNeXNJGo&callback=initMap&libraries=places" async defer></script>
    </body>
</html>
