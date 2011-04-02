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
	var q =  "select id, first_name, last_name, user_name, password_salt,"
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

//##
//ROUTE: ROOT '/status' (GET)
//##
app.get('/status', function(req, res) {
	if (!req.session.user) { 
		res.redirect('/login?redirectUrl=' + unescape('/status'));
	} else {
		var user_id = req.session.user.id;
                var get_current_status = "select * from status where user_id = " + user_id + " ORDER BY id DESC LIMIT 1";
                var get_user_info = "SELECT * FROM user WHERE user_id = " + user_id;
		var get_groups_info = "SELECT group_name, g.id FROM groups AS g JOIN membership AS m ON (g.id = m.group_id) JOIN user AS u ON (m.user_id = u.id) WHERE u.id = " + user_id;
                console.log("get_current_status: " + get_current_status);
                db.query(get_current_status, function(err, results, fields) {
                        console.log(results);
                        var userStatus = results;
			db.query(get_groups_info, function(err, results, fields) {
				var groups_info = results;
                        	db.query(get_user_info, function(err, results, fields) {
                                	res.render('status.ejs', { pageTitle: "status", userStatus: userStatus, groupsInfo: groups_info, userInfo: results } );
                        	});
                       	});
                });
        }
});

//##
//ROUTE: ROOT '/status' (POST)
//##
app.post('/status', function(req, res) {
	if (!req.session.user) {
                res.redirect('/login?redirectUrl=' + unescape('/status'));
        } else {
      		console.log(req.body.user_status);
        	var new_status = "INSERT INTO status (user_id, date, group_id, completed_status, predicted_status) VALUES (" + req.body.user_status.user_id + ", NOW(), " + req.body.user_status.group_id + ", '" + req.body.user_status.completed_status + "', '" + req.body.user_status.predicted_status + "')";
        	console.log("Insert: " + new_status);
        	db.query(new_status, function(err, results, fields) {
                	if (err) {
                        	req.flash('error', "status not updated");
                        	res.redirect('/status');
                	} else {
                        	req.flash('success', "status updated");
                        	res.redirect('/status');
                	}
        	});
	}

});

//get a specific status from the database 
//##
//ROUTE: ROOT '/status/:id' (GET)
//##
app.get('/status/:id', function(req, res) {
	if (!req.session.user) { 
		var redirect_string = '/status/' +  req.params.id;
		res.redirect('/login?redirectUrl=' + unescape(redirect_string));
	} else {
		var user_id = req.session.user.id;
		// note this is allowing anyone in the system to see this...
		var get_selected_status = "SELECT s.id as id, first_name, last_name, date, completed_status, predicted_status  FROM status AS s JOIN user AS u ON (user_id = u.id) WHERE s.id = " + req.params.id + " AND group_id IN (select group_id from membership where user_id = " + req.session.user.id+ ")"; 
                db.query(get_selected_status, function(err, results, fields) {
                	res.render('single_status.ejs', { pageTitle: "status", statusInfo: results } );
                });
        }
});

//get all the status about a specific user
//##
//ROUTE: ROOT '/status/user/:id' (GET)
//##
app.get('/status/user/:id', function(req, res) {
	if (!req.session.user) { 
		var redirect_string = '/status/user/' +  req.params.id;
		res.redirect('/login?redirectUrl=' + unescape(redirect_string));
	} else {
		var user_id = req.session.user.id;
		// note this is allowing anyone in the system to see this...
		var get_selected_status = "SELECT s.id as id, first_name, last_name, date, completed_status, predicted_status  FROM status AS s JOIN user AS u ON (user_id = u.id) WHERE user_id = " + req.params.id + " AND group_id IN (select group_id from membership where user_id = " + req.session.user.id+ ")"; 
		console.log(get_selected_status);
                db.query(get_selected_status, function(err, results, fields) {
			var sortedStatusHash = utils.getStatusHash(results);
                	res.render('user_status.ejs', { pageTitle: "status", statusInfo: sortedStatusHash } );
                });
        }
});


//Start the web server
//console.log("{0} is cool".format("Jeff"));
app.listen(8000);
console.log("Starting server on 0.0.0.0:8000...");
