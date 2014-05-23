describe('app.js', function() {
    var xhr_requests = [];

    beforeEach(function() {
        // Set predictable jsonp callback 
        $.ajaxSetup({
            jsonpCallback: 'test'
        });

        // Fake XHR
        this.xhr = sinon.useFakeXMLHttpRequest();
        
        this.xhr.addFilter(function(method, url) {
            return url.indexOf('/test/fixtures') === 0;
        });
        this.xhr.useFilters = true;

        this.xhr.onCreate = function(xhr) {
            xhr_requests.push(xhr);
        };

        // Fake Timers
        this.timers = sinon.useFakeTimers();

        // JSON Fixtures
        jasmine.getJSONFixtures().fixturesPath = '/test/fixtures'

        // Sandbox
        $('body').append(sandbox({ id: 'test-body' }));
    });

    afterEach(function() {
        $('#test-body').remove();

        this.timers.restore();
        this.xhr.restore();

        xhr_requests = [];
    });

    it('should render a javascript template', function() {
        var context = $.extend(APP_CONFIG, {
            'template_path': 'jst/example.html',
            'config': JSON.stringify(APP_CONFIG, null, 4),
            'copy': JSON.stringify(COPY, null, 4)
        });

        var html = JST.example(context);

        expect(html).toContain('jst/example.html');
    });
});
