describe('tests', function() {
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

    it('should load JST templates', function() {
        expect(window.JST).toBeDefined();
    });

    it('should mock XHR requests', function() {
        $.getJSON('test.json');

        expect(xhr_requests.length).toBe(1);
    });

    it('should load JSON fixtures', function() {
        var fixture = getJSONFixture('example.json');

        expect(fixture).toBeDefined();
        expect(fixture['test']).toEqual('fixture');
    });
});
