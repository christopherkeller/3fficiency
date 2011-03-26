var express = require('express');

var app = express.createServer();

app.get('/', function(req, res) {
	res.send('Hello World!');
}).listen(8000, "127.0.0.1");
