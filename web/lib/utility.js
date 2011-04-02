var crypto = require('crypto')
	, path = require('path')
	, fs = require('fs');

exports.formatString = function(str) {
	for(var i=1;i<arguments.length;i++)
	{
		var exp = new RegExp('\\{' + (i-1) + '\\}','gm');
		arguments[0] = arguments[0].replace(exp,arguments[i]);
	}
	return arguments[0];
}

exports.hash = function(str, hashType, encoding) {
	return crypto
		.createHash(hashType)
		.update(str)
		.digest(encoding || 'hex');
}

exports.uid = function(len) {
	var buffer = []
		, chars = '0987654321abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
		, charlen = chars.length;

	for (var i = len - 1; i >= 0; i--) {
		buffer.push(chars[randomInt(0, charlen - 1)]);
	}

	return buffer.join('');
}

function randomInt(minimum, maximum) {
	return Math.floor(Math.random() * (maximum - minimum + 1)) + minimum;
}

// this will take an array and return a hash array/object:
//
// 	date => array(status, status);
exports.getStatusHash = function(statusHash) {

	var sortedHash = new Array();
	// since we are building a hash which in js is an object lets 
	// set a flag to say that the 'object has some stuff in it'
	// note this flag will be used/tested in the view
	if (statusHash.length == 0) {
		sortedHash.hasStatus = false;
	} else {
		sortedHash.hasStatus = true;
		sortedHash.keys = new Array();
	}		

	for (var i = 0; i < statusHash.length; i++) {
		var date_key = this.formatDate(statusHash[i].date); // this should be a string 1/2/11
		if (sortedHash[date_key] == undefined) {
			sortedHash[date_key] = new Array();
			sortedHash.keys.push(date_key);
			sortedHash[date_key].push(statusHash[i]);
		} else {
			sortedHash[date_key].push(statusHash[i]);
		}
	}

	return sortedHash;
}

exports.formatDate = function(date_string) {

	var ugly_date = new Date(date_string);
	var pretty_date = ugly_date.getMonth() + 1 + "/" + ugly_date.getDate() + "/" + ugly_date.getFullYear();
	return pretty_date;
}
