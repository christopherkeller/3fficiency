var express = require('express');
var app = express.createServer();
var Client = require('mysql').Client, db = new Client();
var path = './database.yml', fs = require('fs'), yaml = require('yaml');
var config = yaml.eval(fs.readFileSync(path).toString());

db.host = config.development.host;
db.user = config.development.user;
db.password = config.development.password;
db.database = config.development.database;
db.connect();

app.configure(function() {
	app.use(express.methodOverride());
	app.use(express.bodyParser());
	app.use(app.router);
 	app.use(express.static(__dirname + '/public'));
	app.set('views', __dirname + '/views');
});

app.get('/', function(req, res) {
	db.query("select * from user", function(err, results, fields) {
		res.render('index.ejs', { pageTitle: "nventio", viewData: results } );
	});
	//res.render('index.ejs', { pageTitle: "nventio", viewData: null } );
});

app.listen(8000);
console.log("Server running @ http://localhost:8000");
