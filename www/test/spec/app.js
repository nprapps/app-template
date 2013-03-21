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
        var html = JST.example({ 'config': 'test', 'template_path': 'test' });

        console.log(html);

        expect(html).toMatch('<code>test</code>');
    });
});
