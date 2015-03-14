
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
		console.log(data);
		completer.options = Object.keys(data);
		completer.repaint();
	});
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
	$(selector).velocity('slideDown');
	
	currentlyVisible = '#screen-'+id;
}

function back() {
	var current = order.indexOf(currentlyVisible.replace('#screen-',''));
	scrollTo(order[current-1]);
}

// misc DOM functions
function domReady() {
	if (document.readyState !== 'complete') return;

	$('.btn-mode-select').on('click', modeChosen);
	$('#btn-back').on('click', back);

	completer = completely(document.getElementById('input-stop'));
	completer.startFrom = 0
	completer.input.style.border = '1px solid #D1D1D1';
	updateCompleter('');
	completer.onChange = updateCompleter;
	console.log('Done');
}

document.addEventListener('readystatechange', domReady);

