$(document).ready(function(){
    mapbox.load(['npr.map-94vv5tn9','npr.us-wildfires'], function(data){
        window.m = mapbox.map('map');
        m.addLayer(data[0].layer);
        m.addLayer(data[1].layer);
        m.setZoomRange(3,9);
        m.interaction.auto();
    
        var width = $(window).width();
        if(width >= 960){
            m.zoom(4);
            m.center({ lat: 40, lon: -108 });
            m.ui.zoomer.add();
        } else if (width >= 650){
            m.zoom(4);
            m.center({ lat: 40, lon: -97 });
            m.ui.zoomer.add();
        } else {
            m.zoom(3);
            m.center({ lat: 40, lon: -97 });
        }
    
        var markerLayer = mapbox.markers.layer();
        markerLayer.factory(function(feature) {
            var dangerCode = feature.properties.dangerCode;
            var level;
            var levelName;
            switch(dangerCode) {
                case -9999:
                    level = 'not-reported'
                    levelName = 'Not reported'
                    break;
                case 1:
                    level = 'low'
                    levelName = 'Low'
                    break;
                case 2:
                    level = 'moderate'
                    levelName = 'Moderate'
                    break;
                case 3:
                    level = 'high'
                    levelName = 'High'
                    break;
                case 4:
                    level = 'very-high'
                    levelName = 'Very high'
                    break;
                case 5:
                    level = 'extreme'
                    levelName = 'Extreme'
                    break;
                default:
                    level = 'not-reported'
                    levelName = 'Not reported'
                    break;
            }
            var cityState = '';
            if(feature.properties.placeCity){
                cityState = feature.properties.placeCity + ', ' + feature.properties.placeState;
            }
            window.newPopup = $('<div class="danger-popup">Wildfire Danger<div class="city-state">' + cityState + '</div><div class="danger-rating danger-' + level + '">' + levelName + '</div><div class="pointer"></div></div>');
            return newPopup[0];
        });
        m.addLayer(markerLayer);    
        $('#find,#find2').click(function(){
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    zoomToPin(position.coords.latitude,position.coords.longitude);
                },
                function(err) {
                    alert('Your location could not be found. Try enabling location services.');
                }
            );
        });
    
        function on_all_loaded(layer, callback) {
            if (layer.requestManager.openRequestCount == 0) {
                callback();
            } else {
                var cb = function() {
                    if (layer.requestManager.openRequestCount > 0) return;
                    else callback();
                    layer.requestManager.removeCallback('requestcomplete', cb);
                }
                layer.requestManager.addCallback('requestcomplete', cb);
            }
        }
            
        function zoomToPin(lat,lon,placeCity,placeState){
            //set the center and zoom in                    
            m.center({
                lon: lon,
                lat: lat
            });
            m.zoom(8);
            markerLayer.features([]);
            m.refresh();
        
            on_all_loaded(m.getLayerAt(0), function() {
                m.interaction.screen_feature({
                    x: m.dimensions.x / 2,
                    y: m.dimensions.y / 2 }, function(ft) {
                    //pass an empty array to clear the features
                
                    var dangerCode;
                    if(ft) {
                        dangerCode = ft.GRID_CODE;
                    } else {
                        dangerCode: -9999;
                    }
                    markerLayer.add_feature({
                        geometry: {
                            coordinates: [
                                lon,
                                lat]
                        },
                        properties: {
                            dangerCode: dangerCode,
                            placeCity: placeCity,
                            placeState: placeState
                        }
                    });
                    m.panBy(0,60);
                });
            });
        }
            
        $('#search').submit(function(e){
            e.preventDefault();
            geocode(encodeURIComponent($('#search input').val()));
        });
        $('#search2').submit(function(e){
            e.preventDefault();
            geocode(encodeURIComponent($('#search2 input').val()));
        });
            
        function geocode(query){
            $.ajax({
               url: 'http://open.mapquestapi.com/nominatim/v1/search?format=json&countrycodes=us&limit=1&addressdetails=1&q=' + query,
               cache: false,
               dataType: 'jsonp',
               jsonp: 'json_callback',
               success: function(response){
                   value = response[0];
                   if (value === undefined) {
                       alert('That location could not be found. Try using a city, state, Zip Code or mailing address.');
                   } else { 
                       zoomToPin(value.lat, value.lon, value.address[value.type], value.address.state);
                   }
               }
            });
        }

        $("#about").click(function(){
            if($(".modal-body").children().length < 1 ) {
                $(".modal h3").text($(".legend-contents .headline").text());
                $(".legend-contents .headline").hide();
                $(".legend-contents").clone().appendTo(".modal-body");
            }
        });
    
        if(window.location.search.indexOf("embed") > 0) {
            $("#nav").hide();
            $("#embed-nav").show();
            $("#topper").addClass("embedded");
            $("#embed-nav").click(function(){window.open('http://apps.npr.org/fire-forecast');});
        }    

        //for old browsers and for IE in a frame
        if (!navigator.geolocation) {
            $("#find,find2").hide();
        }
    });
});
