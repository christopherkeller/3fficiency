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

