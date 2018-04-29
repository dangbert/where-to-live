$(document).ready(function() {
    $( "#temp-range" ).slider({
        range: true,
        min: 5,
        max: 90,
        values: [ 5, 90 ],
        slide: function( event, ui ) {
            if (ui.values[ 0 ] > 70)
                ui.values[ 0 ] = 70;

            if (ui.values[ 1 ] < 20)
                ui.values[ 1 ] = 20;

            $("#low-temp-value").text(ui.values[ 0 ]);
            $("#high-temp-value").text(ui.values[ 1 ]);
        }
    });



    $( ".detail-slider" ).each(function(){
        $(this).slider({
            value:100,
            min: 0,
            max: 100,
            step: 1,
            slide: function( event, ui ) {
                $(this).next(".detail-slider-value").text(ui.value);
            }
        });
    });

    // $( ".climate-slider" ).each(function(){
    //     $(this).slider({
    //         value:100,
    //         min: 0,
    //         max: 100,
    //         step: 1,
    //         slide: function( event, ui ) {
    //             $(this).next("#climate-slider-value").text(ui.value);
    //         }
    //     });
    // });
    $( "#climate-dropdown" ).change(function(){
        if ($(this).val() == 'Hotter'){
            $("#rain-dropdown-").show();
            $("#snow-dropdown").hide();
        } else if ($(this).val() == "Colder"){
            $("#rain-dropdown").hide();
            $("#snow-dropdown").show();
        } else {
            $("#rain-dropdown").show();
            $("#snow-dropdown").show();
        }
    });

    $( ".commute-slider" ).slider({
        value:60,
        min: 0,
        max: 60,
        step: 1,
        slide: function( event, ui ) {
            $(this).next("#commute-slider-value").text(ui.value);
        }
    });

    $(".toggle-menu-option").each(function(){
        $(this).prop('checked', true);
    });

    $(".checkbox").on("change", function(){
        $(this).next(".detailed-criteria").toggle();
        setActiveSearch();
    });
    setActiveSearch();
    setScope()

    $(".toggle-menu-option").each(function(){
        $(this).click();
    });
    
    $(function () {
      $('[data-toggle="tooltip"]').tooltip()
    });

    $("#search-button").on("click", function() {
        // make a POST request to our search script
        // TODO: don't hardcode the data (use the search inputs)
        console.log("doing search");
        $.ajax({
            type: "POST",
            url: "/controllers/search.php",
            contentType: "application/json",
            dataType: "json",
            data: JSON.stringify({
              "schools": {
                "enabled": true,
                "value": 1
              },
              "transportation": {
                "enabled": true,
                "value": 1
              },
              "crime": {
                "enabled": true,
                "value": 1
              },
              "recreation": {
                "enabled": true,
                "value": {
                    "has_biking": false,
                    "has_climbing": false,
                    "has_camping": true,
                    "has_hiking": false,
                    "has_hunting": false,
                    "has_wilderness": false,
                    "has_swimming": false
                }
              },
              "climate": {
                "enabled": true,
                "value": {
                  "temperature": 0,
                  "precipitation": 1,
                  "snowfall": 1
                }
              },
              "healthcare": {
                "enabled": true,
                "value": 0
              },
              "commute": {
                "enabled": true,
                "value": 47
              }
            }),
            success: function(resp) {
                console.log(resp);
                // TODO: display these results on the map
            },
            error: function(resp) {
                console.log(resp);
            }
        });
    });
});

function setActiveSearch(){
    var active = "<div class=\"columns\"><ul>";
    $(".toggle-menu-option").each(function(){
        if($(this).is(':checked')){
                active += "<li>" + $(this).attr("id") + "</li> ";
        }
    });
    active += "</ul></div>";
    $("#active-criteria").html(active.slice(0, -2));
}

function setScope(){
    var scope = "states";
    var otherScope = "counties";

    if (scope == "states")
        var direction = "in";
    else
        var direction = "out";

    $("#scope").html("Currently searching for matching <b>" + scope + "</b>. Zoom " + direction + " on the map to change search to <b>" + otherScope + "</b>.");
}

function openNav() {
    document.getElementById("mySidenav").style.width = "250px";
    document.getElementById("main").style.marginLeft = "250px";
}

function closeNav() {
    document.getElementById("mySidenav").style.width = "0";
    document.getElementById("main").style.marginLeft= "0";
}

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

    // display a point on the map (for testing)
    var myLatLng= {lat: 39.255, lng: -76.711};
    var marker = new google.maps.Marker({
            position: myLatLng,
            map: map
    });


    // attempt to get user location with W3C Geolocation (Preferred). see: tinyurl.com/gmproj3
//    var initialLocation;
//    if(navigator.geolocation) {
//        navigator.geolocation.getCurrentPosition(function(position) {
//            initialLocation = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
//            map.setCenter(initialLocation);
//            map.setZoom(11);
//        });
//    }
}
