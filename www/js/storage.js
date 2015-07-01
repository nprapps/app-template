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

    return {
        'set': set,
        'get': get,
        'deleteKey': deleteKey,
        'setTTL': setTTL,
        'getTTL': getTTL
    }
}());
