/* Settings */
var MY_GLOBAL_SETTINGS = 'foo';

function my_function() {
	alert("called");
}

// Example of rendering a precompiled template
$("#sample-content").html(window.JST['example']({ name: 'example' }));
