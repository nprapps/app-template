module.exports = function(grunt) {

    // Project configuration.
    grunt.initConfig({
        less: {
            all: {
                files: {
                    'www/css/app.css': 'less/*.less'
                }
            },
        },
        jst: {
            all: {
                options: {
                    processName: function(filename) {
                        return filename.split("/").pop().split(".")[0];
                    }
                },
                files: {
                    'www/js/templates.js': ['www/jst/*.html']
                }
            }
        },
        watch: {
            files: ['less/*.less', 'www/jst/*.html', 'www/css/*.css', 'www/js/*.js'],
            tasks: 'default'
        }
    });

    grunt.loadNpmTasks('grunt-contrib-less');
    grunt.loadNpmTasks('grunt-contrib-jst');

    // Task to compile webassets
    grunt.registerTask('webassets', 'Compile webassets.', function() {
        var done = this.async();
        var exec = require('child_process').exec;

        exec('webassets -m assets_env build', function callback(error, stdout, stderr) {
            done();
        });
    });

    // Default task.
    grunt.registerTask('default', 'less jst webassets');

};
