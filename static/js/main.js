
//console.log("Hello, World!");

// 1. select mode
var mode;
var order = ['initial', 'pick-journey'];
function modeChosen(ev) {
	//window.lastEvent = ev;
	mode = ev.target.id.split('-')[2];
	//window.location.hash = '#pick-journey';
	scrollTo('pick-journey');

}

// pick journey mode
var completer;
var currentStopsCache;
function updateCompleter(txt) {
	$.getJSON('/api/stops/' + encodeURIComponent(txt), function(data) {
		currentStopsCache = data;
		//console.log(data);
		completer.options = Object.keys(data);
		completer.repaint();
	});
}

function onCompleterEnter() {
	completer.hideDropDown();
	$.getJSON('/api/stops/id/' + encodeURIComponent(currentStopsCache[completer.getText()]), function(data) {
		//$('#selected-stop-info').html('<ul><li>id: ' + data.id + '</li><li>name: ' + data.name + '</li></ul>');
		dropMapPin(data.name, new google.maps.LatLng(Number(data.lat), Number(data.long)));
	});
	console.log('return');
}

// navigation
var currentlyVisible = '#screen-initial';
function scrollTo(id) {
	//$(id).velocity('scroll');
	//console.log(id);
	var selector='#screen-'+id;
	if (id != 'initial') {
		selector += ',#btn-back';
	} else {
		currentlyVisible += ',#btn-back';
	}
	$(currentlyVisible).velocity('slideUp');
	$(selector).velocity('slideDown', {
		complete: function() {
			resizeMap(); // weird stuff happens otherwise
		}
	});
	
	currentlyVisible = '#screen-'+id;
}

function back() {
	var current = order.indexOf(currentlyVisible.replace('#screen-',''));
	scrollTo(order[current-1]);
}

// google maps
function initialiseMap() {
	window.map = new google.maps.Map(document.getElementById('map-canvas'));
	map.setZoom(12);
	resizeMap();
	map.setMapTypeId(google.maps.MapTypeId.ROADMAP);
}

function resizeMap() {
	if (!window.google) return;
	google.maps.event.trigger(window.map, 'resize');
	map.setCenter(new google.maps.LatLng(-33.87601919093802, 151.218299));	
}

function dropMapPin(name, latLng) {
	var marker = new google.maps.Marker({
		position: latLng,
		map: map,
		title: name,
		animation: google.maps.Animation.DROP
	});
}

// misc DOM functions
function domReady() {
	if (document.readyState !== 'complete') return;

	$('.btn-mode-select').on('click', modeChosen);
	$('#btn-back').on('click', back);

	// load the google API key
	$.getJSON('/api/key', function(obj) {
		var script = document.createElement('script');
		script.type = 'text/javascript';
		script.src = '//maps.googleapis.com/maps/api/js?callback=initialiseMap&key=' + obj.key;
		document.body.appendChild(script);
		console.log('[loaded maps api]');

	})

	completer = completely(document.getElementById('input-stop'));
	completer.startFrom = 0
	completer.input.style.border = '1px solid #D1D1D1';
	updateCompleter('');
	completer.onChange = updateCompleter;
	completer.onEnter = onCompleterEnter;
}

document.addEventListener('readystatechange', domReady);

