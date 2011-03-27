//Setup namespaces and imports
var express = require('express');
var app = express.createServer();
var Client = require('mysql').Client, db = new Client();
var MemoryStore = require('connect').session.MemoryStore;
var csrf = require('express-csrf');  		//npm install express-csrf
var hash = require('node_hash');		//npm install node_hash

//Read our database connection from yaml and establish connection
var path = './database.yml', fs = require('fs'), yaml = require('yaml');
var config = yaml.eval(fs.readFileSync(path).toString());
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

	res.render('login.ejs', { pageTitle: 'login' });
});

app.post('/login', function(req, res) {
	//TODO: Refactor this query shit out into a class or something
	var q = "select id, first_name, last_name, user_name, group_id from user where user_name     = ? limit 1";
	params = req.body;
	//Get the user from the database based on username
	db.query(q, [params.username], function(err, results, fields) {
		if (err || results.length == 0) {
			//Flash on error
			req.flash('error', 'A problem occured while logging in.');
			res.redirect('/login');
		} else {
			//TODO: Get the password hash, salt from database
			//TODO: Hash the given password and compare with db
			//TODO: If everything is good, consider the user authenticated
			console.log("Results:" + results);
		}
	});
});


//##
//ROUTE: ROOT '/' (GET)
//##
app.get('/', function(req, res) {
	if (!req.session.user) { 
		res.redirect('/login');
	} else {
		db.query("select * from user", function(err, results, fields) {
			res.render('index.ejs', { pageTitle: "nventio", viewData: results } );
		});
	}
});

//Start the web server
app.listen(8000);
console.log("Starting server on 0.0.0.0:8000...");
