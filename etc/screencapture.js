var page = require('webpage').create();
var system = require('system');
page.clipRect = {'top': 0, 'left': 0, 'width': 1024, 'height': 768};
page.viewportSize = { width: 1024, height: 768 };
page.open('http://localhost:8000/', function () {
    page.render(system.args[1]);
    phantom.exit();
});
