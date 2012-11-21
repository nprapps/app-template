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
            files: ['less/*.less', 'www/jst/*.html'],
            tasks: 'default'
        }
    });

    grunt.loadNpmTasks('grunt-contrib-less');
    grunt.loadNpmTasks('grunt-contrib-jst');

    // Default task.
    grunt.registerTask('default', 'less jst');
};
