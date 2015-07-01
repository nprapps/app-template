var STORAGE = (function() {
    var set = function(key, value) {
        simpleStorage.set(APP_CONFIG.PROJECT_SLUG + '-' + key, value);
    }

    var get = function(key) {
        var value = simpleStorage.get(APP_CONFIG.PROJECT_SLUG + '-' + key);
        return value;
    }

    var deleteKey = function(key) {
        simpleStorage.deleteKey(APP_CONFIG.PROJECT_SLUG + '-' + key);
    }

    var setTTL = function(key, ttl) {
        simpleStorage.setTTL(APP_CONFIG.PROJECT_SLUG + '-' + key, ttl)
    }

    var getTTL = function(key) {
        var ttl = simpleStorage.getTTL(APP_CONFIG.PROJECT_SLUG + '-' + key);
        return ttl;
    }

    var testStorage = function() {
        var test = STORAGE.get('test');
        if (test) {
            STORAGE.deleteKey('test');
        }
        console.log(simpleStorage.index()); // empty array
        console.log(STORAGE.get('test')); // undefined

        STORAGE.set('test', 'haha');
        console.log(STORAGE.get('test'), STORAGE.getTTL('test')); // haha, Infinity

        STORAGE.setTTL('test', 1000);
        console.log(STORAGE.getTTL('test')); // 999 or 1000 or something close

        console.log(simpleStorage.index()); // one element array
        simpleStorage.flush();
        console.log(simpleStorage.index()) // empty array
    }

    return {
        'set': set,
        'get': get,
        'deleteKey': deleteKey,
        'setTTL': setTTL,
        'getTTL': getTTL,
        'testStorage': testStorage
    }
}());
