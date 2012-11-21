module.exports = function(grunt) {

    // Project configuration.
    grunt.initConfig({
        min: {
            header_js: {
                src: [
                    'js/lib/jquery-1.8.2.min.js',
                    'js/lib/modernizr.js',
                    'js/responsive-ad.js'
                ],
                dest: 'www/js/app-header.min.js'
            },
            footer_js: {
                src: [
                    'js/lib/underscore-min.js',
                    'js/lib/moment.min.js',
                    'bootstrap/js/bootstrap.min.js',
                    'js/lib/jquery.tablesorter.min.js',
                    'js/templates.js',
                    'js/app.js'
                ],
                dest: 'www/js/app-footer.min.js'
            }
        },
        concat: {
            css: {
                src: [
                    'www/bootstrap/css/bootstrap.min.css',
                    'www/bootstrap/css/bootstrap-responsive.min.css',
                    'www/css/tablesorter.css',
                    'www/css/app.css'
                ],
                dest: 'www/css/app.min.css'
            }
        },
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

    // Default task.
    grunt.registerTask('default', 'less jst min concat');

};
