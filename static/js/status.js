

jQuery(document).ready(function() {
	var group = '';
	var time_frame = '';	

	/* what gets fired off when a group button is pressed on the homepage (/) */
	jQuery(".button").click(function() {
		group = jQuery(this).attr("id");
		console.log(group);
		if (time_frame == '') {
			time_frame = jQuery("#time_frame").val();
		}
		var status_url = "/group/" + group + "/status/" + time_frame +  "/json/";
		jQuery.get(status_url, function(data) {
			build_status_list(data);
		});
		jQuery("#time_select").slideDown('slow');	
	});

	/* what gets fired off when the time frame drop down appears (after the button has been clicked */
	jQuery("#time_frame").change(function() {
		time_frame = jQuery(this).val();
		var status_url = "/group/" + group + "/status/" + time_frame +  "/json/";
		jQuery.get(status_url, function(data) {
			build_status_list(data);
		});
	});

	$(function() {
		$( "#slider" ).slider();
	})

});


/* data looks like this:
	data.keys = Array of keys
	data[key] = Array of status
*/
function build_status_list(data) {
	

	if (data.keys.length == null) {
		return;
	}

	html = '<ul>';
	jQuery.each(data.keys, function(index) {
		html += "<li>" +  data.keys[index];
		html += "<ul>";
		for (var i = 0; i < data[data.keys[index]].length; i++) {
			// "Christopher Keller": [["03/29/2011", "yes i got that done"]]
			// 0 == date and 1 == status
			//html += "<li>" + data[index][i][0] + " " + data[index][i][1] + "</li>";
			html += "<li>" + data[data.keys[index]][i][0] + " " + data[data.keys[index]][i][1] + "</li>";
		}
		html += "</ul>";	
		html += "</li>";
	});
	html += '</ul>';
	jQuery("#display_status").html(html).slideDown('slow');


}
