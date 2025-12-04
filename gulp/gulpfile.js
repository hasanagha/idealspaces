var gulp         = require('gulp');
var sass         = require('gulp-sass');
var concat       = require('gulp-concat');
var browsersync  = require('browser-sync').create();
var webserver    = require('gulp-webserver');
var minify       = require('gulp-minifier');
var minifyCSS    = require('gulp-minify-css');
var autoprefixer = require('gulp-autoprefixer');
var uglify       = require('gulp-uglify');

var paths_for_css_files = [
  '../common_static/css/*.css',
];

var paths_for_js_files = [
  '../common_static/libs/*.js',
  '../common_static/libs/**/*.js',
];

var path_for_sass_files = '../common_static/scss/*.scss';
var path_for_sass_files_to_watch = [
  '../common_static/scss/*.scss',
  '../common_static/scss/**/*.scss',
  '../common_static/scss/**/**/*.scss',
];
var path_for_distribution = '../common_static/dist';

// 
gulp.task('sass', ['minifycss'], function(){
  return gulp.src(path_for_sass_files)
    .pipe(sass()) // Using gulp-sass
    .pipe(gulp.dest('../common_static/css'));
});

gulp.task('browsersync', function() { 
  browsersync.init({
    proxy: "localhost:7000",
  });
});

// Watch JS/Sass files
gulp.task('watch', function(done) {
  gulp.watch(path_for_sass_files_to_watch, ['sass']);
  // gulp.watch(paths_for_js_files, ['minifyjs']);
  done();
});

gulp.task('webserver', function() {
  gulp.src('app')
    .pipe(webserver({
      livereload: true,
      directoryListing: true,
      open: true
    }));
});

gulp.task('minifycss', function() {
  var file_name = "style.min.css";

  if (process.argv[3] == '-p') {
    return gulp.src(paths_for_css_files)
      .pipe(minifyCSS())
      .pipe(autoprefixer('last 2 version', 'safari 5', 'ie 8', 'ie 9'))
      // .pipe(concat(file_name))
      .pipe(gulp.dest(path_for_distribution));
  } else {
    return gulp.src(paths_for_css_files)
      .pipe(autoprefixer('last 2 version', 'safari 5', 'ie 8', 'ie 9'))
      .pipe(concat(file_name))
      .pipe(gulp.dest(path_for_distribution))
      .pipe(browsersync.reload({
        stream: true
      }));
  }
});

gulp.task('minifyjs', function() {
  var file_name = "scripts.min.js";

  if (process.argv[3] == '-p') {
    gulp.src(paths_for_js_files).pipe(concat(file_name)).pipe(uglify()).pipe(gulp.dest(path_for_distribution));
  } else {
    gulp.src(paths_for_js_files).pipe(concat(file_name)).pipe(gulp.dest(path_for_distribution)).pipe(browsersync.reload({
      stream: true
    }));
  }
});

gulp.task('build', ['minifycss']);
gulp.task('default', ['sass', 'minifycss', 'watch', 'browsersync']);
