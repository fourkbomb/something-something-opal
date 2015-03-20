
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
var stopFrom;
var stopTo;
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
		if (pins.length > 0 && stopFrom) {
			stopTo = data;
			drawLine(stopFrom, stopTo);
			stopFrom = stopTo;
		} else {
			stopFrom = data;
		}
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
var pins = [];
var lines = [];
function initialiseMap() {
	window.map = new google.maps.Map(document.getElementById('map-canvas'));
	map.setZoom(12);
	resizeMap();
	map.setMapTypeId(google.maps.MapTypeId.ROADMAP);
	// magic functions! source: http://stackoverflow.com/a/5239323
	google.maps.LatLng.prototype.kmTo = function(a){ 
	    var e = Math, ra = e.PI/180; 
	    var b = this.lat() * ra, c = a.lat() * ra, d = b - c; 
	    var g = this.lng() * ra - a.lng() * ra; 
	    var f = 2 * e.asin(e.sqrt(e.pow(e.sin(d/2), 2) + e.cos(b) * e.cos 
	    (c) * e.pow(e.sin(g/2), 2))); 
	    return f * 6378.137; 
	}

	google.maps.Polyline.prototype.inKm = function(n){ 
	    var a = this.getPath(n), len = a.getLength(), dist = 0; 
	    for (var i=0; i < len-1; i++) { 
	       dist += a.getAt(i).kmTo(a.getAt(i+1)); 
	    }
	    return dist;
	}
}

function resizeMap() {
	if (!window.google) return;
	google.maps.event.trigger(window.map, 'resize');
	map.setCenter(new google.maps.LatLng(-33.87601919093802, 151.218299));	
}

function dropMapPinBoring(latLng) {
	var marker = new google.maps.Marker({
		position: latLng,
		map: map,
		title: latLng.lat + ',' + latLng.lng
	});
	pins.push(marker);	
}

function dropMapPin(name, latLng) {
	var marker = new google.maps.Marker({
		position: latLng,
		map: map,
		title: name,
		animation: google.maps.Animation.DROP
	});
	pins.push(marker);
}

function undo() {
	var lastMarker = pins.pop();
	var lastLine = lines.pop();
	lastLine.setMap(null);
	lastMarker.setMap(null);
}

function drawLine(from, to) {
	//dropMapPin(from.name, {lat: from.lat, long: from.long});
	//dropMapPin(to.name, {lat: to.lat, long: to.long});
	from.lat = Number(from.lat);
	from.lng = Number(from.long);
	to.lng = Number(to.long);
	to.lat = Number(to.lat);
	var path = new google.maps.Polyline({
		path: [from, to],
		geodesic: true,
		strokeColor: '#FF0000',
		strokeOpacity: 1.0,
		strokeWeight: 2
	});
	path.setMap(map);
	lines.push(path);
	calculateFare(from, to, path);
	//$('#lines-distance').html($('#lines-distance').html() + from.name + ' - ' + to.name + ': ' + path.inKm(path).toFixed(2) + 'km<br />');
}

function getTestData() {
	$.getJSON('/static/data.json', function(data) {
		window.allStops = data;
		console.log('loaded ' + data.length + ' stops');
	});
}

function showShape(shpID) {
	$.getJSON('/api/shape/' + encodeURIComponent(shpID), function(data) {
		console.log('loaded');
		data.data = data.data.map(function (e) {
			return {lat: Number(e[0]), lng: Number(e[1])};
		});
		window.shapeData = data.data;
		drawPoly(data.data);
		data.data.forEach(dropMapPinBoring);
	});
}

function drawPoly(pts) {
	var path = new google.maps.Polyline({
		path: pts,
		geodesic: true,
		strokeColor: '#FF0000',
		strokeOpacity: 1.0,
		strokeWeight: 2
	});
	path.setMap(map);
}

// fare calculation
var currentTotalFare = 0.0;
var constituentFares = [];
var totalDistance = 0.0;

var fares = {
	'bus': {
		3: 2.1,
		8: 3.5,
		default: 4.5
	},
	'ferry': {
		9: 5.74,
		default: 7.18
	},
	'train': {
		10: 3.38,
		20: 4.20,
		35: 4.82,
		65: 6.46,
		default: 8.3
	}
};

function calculateFinalFare(from, to, distance) {
	var sectionFare = 0;
	if (from.type == to.type) {
		sectionFare = fares[from.type].default;
		if (distance == 0) {
			sectionFare = 0.0;
		} else {
			var keys = Object.keys(fares[from.type]);
			delete keys[keys.indexOf('default')];
			var i;
			var best = 256;
			for (i = 0; i < keys.length; i++) {
				var key = keys[i];
				if (key < best && distance < key) {
					best = key;
				}
			}
			if (best !== 256) {
				sectionFare = fares[from.type][best];
			}
			if (mode !== 'adult') sectionFare /= 2;
			//sectionFare = sectionFare.toFixed(2);
		}
		totalDistance += distance;
		currentTotalFare += sectionFare;
		constituentFares.push(sectionFare);
		sectionFare = sectionFare.toFixed(2);
	} else {
		sectionFare = '--';
	}
	var newEntry = document.createElement('tr');
	newEntry.innerHTML = '<td>' + from.name + '</td><td>' + to.name + '</td><td> ' + distance.toFixed(2) + 'km</td><td>$' + sectionFare + '</td>';
	$('#fare-total').before('<tr>' + newEntry.innerHTML + '</tr>');
	updateTotal();
}

function calculateFare(from, to, path) {
	if (from.type === 'train' && to.type === 'train') {
		//console.error('TODO: train ticketing');
		getTrainDistance(from, to);
		return;
	}
	var distance = path.inKm(path); // TODO trips within an hour of each other count as 1
	calculateFinalFare(from, to, distance);
	
}

function updateTotal() {
	$('#distance-total').text(totalDistance.toFixed(2) + 'km');
	$('#cost-total').text('$' + currentTotalFare.toFixed(2));
}

function getTrainDistance(from, to) {
	if (!from.id.startsWith('CR_') || !to.id.startsWith('CR_')) {
		console.error('Not a train trip: ' + from.id + ' -> ' + to.id);
		return;
	}
	$.getJSON('/api/distance/train/' + from.id + '/' + to.id, function(data) {
		calculateFinalFare(from, to, data.dist/1000);
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

