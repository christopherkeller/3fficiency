//Setup namespaces and imports
var express = require('express');
var path = require('path');
var fs = require('fs');
var yaml = require('yaml');
var app = express.createServer();
var Client = require('mysql').Client, db = new Client();
var MemoryStore = require('connect').session.MemoryStore;
var csrf = require('express-csrf');

require.paths.unshift('.');
var utils = require('utility');

console.log(utils.hash('this is a string', 'sha1'));

//Read our database connection from yaml and establish connection
var dbFile = path.join(path.dirname(__filename),'database.yml')
var config = yaml.eval(fs.readFileSync(dbFile).toString());
db.host = config.development.host;
db.user = config.development.user;
db.password = config.development.password;
db.database = config.development.database;
db.connect();

//Setup our helpers, this stuff is visible in the view as a variable
app.dynamicHelpers({
	flash: function(req) { 
		flash = req.flash();
		return flash;
	},
	csrf: csrf.token,
	current_user: function(req) {
		return req.session.user;
	}
});

//Configure the various middleware functionality, view directory and routing.
app.configure(function() {
	app.set('views', __dirname + '/views');
	app.use(express.static(__dirname + '/public'));
	app.use(express.logger());
	app.use(express.cookieParser());

	//TODO: This is not very scalable, probably want to use Redis for storing session
	app.use(express.session({
		secret: 'string'
		, store: new MemoryStore( {reapInterval: 60000 * 10} ) 
	}));

	app.use(express.methodOverride());
	app.use(express.bodyParser());
	app.use(app.router);
	app.use(csrf.check());
	
	//TODO: This shouldn't be on in production, look at configure('development')
	app.use(express.errorHandler({
		dumpExceptions: true
		, showStack: true
	}));
});

//##
//ROUTE: LOGIN '/login' (GET,POST)
//##
app.get('/login', function(req, res) {
	if (req.session.user) {
		req.flash('success', "Authenticated as #{req.session.user.username}");
		res.redirect('/');
	}

	res.render('login.ejs', { pageTitle: 'login', action: req.url  });
});

app.post('/login', function(req, res) {
	console.log(req.url);
	//TODO: Refactor this query shit out into a class or something
	var q =  "select id, first_name, last_name, user_name, group_id, password_salt,"
	q += "password_hash from user where user_name = ? limit 1";
	params = req.body;
	//Get the user from the database based on username
	db.query(q, [params.username], function(err, results, fields) {
		if (err || results.length == 0) {
			//Flash on error, don't authenticate
			req.flash('error', 'A problem occured while logging in.');
			res.redirect('/login');
		} else {
			var salted_pass = results[0].password_salt + params.password;
			var hashed_password = utils.hash(salted_pass, 'sha1');
			if (hashed_password == results[0].password_hash) {
				var url = require('url').parse(req.url, true);
				req.session.user = results[0];
				res.redirect(url.query.redirectUrl);
			} else {
				req.flash('error', 'A problem occured while logging in.');
				res.redirect('/login');
			}
		}
	});
});


//##
//ROUTE: ROOT '/' (GET)
//##
app.get('/', function(req, res) {
	//TODO: We need a way to do precondition filters.  I don't want to have to write
	// 	the logic for this each time.
	if (!req.session.user) { 
		res.redirect('/login?redirectUrl=' + unescape('/'));
	} else {
		console.log(req.session.user);
		db.query("select * from user", function(err, results, fields) {
			res.render('index.ejs', { pageTitle: "nventio", viewData: results } );
		});
	}
});

//Start the web server
app.listen(8000);
console.log("Starting server on 0.0.0.0:8000...");
