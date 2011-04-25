String.prototype.startsWith = function (prefix) {
  	return this.toLowerCase().indexOf(prefix.toLowerCase()) == 0;
};

String.prototype.replaceAll = function (source, target) {
	return this.replace(new RegExp(source, "g"), target);
};

String.prototype.format = function() {
	var formatted = this;
    	for (var i = 0; i < arguments.length; i++) {
        	var regexp = new RegExp('\\{'+i+'\\}', 'gi');
        	formatted = formatted.replace(regexp, arguments[i]);
    	}
    	return formatted;
}
