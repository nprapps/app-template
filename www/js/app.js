var IS_MOBILE = Modernizr.touch;

var MIN_ZOOM = 14;
var MAX_ZOOM = 19;

var MIN_LAT = 35.2473;  // South
var MAX_LAT = 35.3828;  // North
var MIN_LON = -97.6177; // West
var MAX_LON = -97.4254; // East

var window_width;

$(function() {
    // No box ad when we have adhesion, so #main-content gets 12 columns
    if (window.innerWidth <= 1024){
        $('#main-content').removeClass('col-md-8').addClass('col-md-12');
    }

    window_width = $('body').width();
    
    if (window_width < 768) {
        IS_MOBILE = true;
    }

    var southwest = new L.LatLng(MIN_LAT, MIN_LON);
    var northeast = new L.LatLng(MAX_LAT, MAX_LON);
    var bounds = new L.LatLngBounds(southwest, northeast);

    var map = L.mapbox.map('map', null, {
        minZoom: MIN_ZOOM, 
        maxZoom: MAX_ZOOM,
        maxBounds: bounds 
    });

    L.control.scale().addTo(map);
        
    var base_layer = L.tileLayer('http://mw1.gstatic.com/crisisresponse/2013/2013-oklahoma-tornado/digitalglobe/OK_PO_1194054_GE1_2013_05_23_maptiles/{x}_{y}_{z}.png')
    var info_layer = L.mapbox.tileLayer('npr.ok-moore-tornado-satellite');
    var info_grid = L.mapbox.gridLayer('npr.ok-moore-tornado-satellite');
    
    map.addLayer(base_layer);
    map.addLayer(info_layer);
    map.addLayer(info_grid);
    
    function update_info_boxes(latlng){
        var $info_boxes = $('.info-box');

        info_grid.getData(latlng,function(data){
            if(data){
                var html = '';
                if(data.location) {
                    html += '<p class="poi">' + data.location + '</p>';                    
                }
                if(data.locationad) {
                    html += '<p class="locationad">' + data.locationad + '</p>';                    
                }
                $info_boxes.html(html);
            }
        });
    }
    
    if (IS_MOBILE) {
        map.setView([35.338, -97.486], 14);
        
        var $info_bar = $('#info-bar');
        
        map.on('click', function(e){
            update_info_boxes(e.latlng);
        });
        
        $('#about').click(function(){
            if($('.modal-body').children().length < 1 ) {
                $('.legend-contents').clone().appendTo('.modal-body');
            }
        });
    } else {
        map.setView([35.325, -97.486], 14);
    }
});
