$(document).ready(function() {
    console.log("jquery ready");
});

$("#search-button").on("click", function() {
    // make a POST request to our search script
    $.ajax({
        type: "POST",
        url: "/search.php",
        data: {
            "name": "code fury!"
        },
        success: function(resp) {
            alert(resp);
        },
        error: function(resp) {
            console.log(resp);
        }
    });
});

$("#close-nav").on("click", function() {
    closeNav();
});

function openNav() {
    document.getElementById("mySidenav").style.width = "450px";
}

function closeNav() {
    document.getElementById("mySidenav").style.width = "0";
}


// callback when google maps api loads
function initMap() {
    map = new google.maps.Map(document.getElementById('map'), {
        center: {lat: 37.09024, lng: -100.712891}, //initially centered in the middle of the US, quickly replaced with current location
        zoom: 4
//        mapTypeId: google.maps.MapTypeId.ROADMAP
    });


    // see getBounds() from: https://developers.google.com/maps/documentation/javascript/reference/3/#Map
    map.addListener('bounds_changed', function () {
        console.log(map.getBounds());
    });
    
    
    // attempt to get user location with W3C Geolocation (Preferred). see: tinyurl.com/gmproj3
    var initialLocation;
    if(navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            initialLocation = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
            map.setCenter(initialLocation);
            map.setZoom(11);
        });
    }
}
