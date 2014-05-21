
window.map_pins = []

function pageloaded() {
	if(geo_position_js.init()) geo_position_js.getCurrentPosition(function(location){
		window.gps_lat = location['coords']['latitude'];
		window.gps_lon = location['coords']['longitude'];
				
		// use "Current Location" in the submit poster form
		$('input[name="location-lat"]').val(window.gps_lat);
		$('input[name="location-lon"]').val(window.gps_lon);
		
		location_field = $('input[name="filming-location"]');
		location_field.attr('placeholder', "Current Location");
		location_field.addClass('current-location-placeholder')
	}, function(){});
	
	window.map = new google.maps.Map($("#map_canvas")[0], {
		center: new google.maps.LatLng(40.755,-73.955),
		zoom: 12,
		mapTypeId: google.maps.MapTypeId.ROADMAP
	});
	window.infowindow = new google.maps.InfoWindow();

	//drop pins
	var pins = window.map_pins;
	for(var i=0;i<pins.length;i++) {
		var marker = new google.maps.Marker({
			position: new google.maps.LatLng(pins[i].lat, pins[i].lon),
			map: window.map
		});

		google.maps.event.addListener(marker, 'click', (function(marker, pin) {
			return function() {
				infowindow.setContent(pin.info_content);
				infowindow.open(window.map, marker);
			}
		})(marker, pins[i]));
	}
	
	//If it's the only pin on the map, center+zoom on it
	if (pins.length == 1) {
		var point = new google.maps.LatLng(pins[0].lat, pins[0].lon)
		window.map.setCenter(point);
		window.map.setZoom(16);
	}
}
