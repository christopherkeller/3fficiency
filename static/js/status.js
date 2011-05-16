

jQuery(document).ready(function() {
	var group = '';
	var time_frame = '';	

	/* what gets fired off when a group button is pressed on the homepage (/) */
	jQuery(".groups").click(function() {
		// need to make the button active
		jQuery(".groups").removeClass("active");
		jQuery(this).addClass("active");
		group = jQuery(this).attr("id");
		time_frame = $( "#slider" ).slider( "option", "value" );

		if (time_frame == 0) {
			time_frame = 1;
			$("#time_display").html(" last " + time_frame + " day of " + group);
		} else {
			$("#time_display").html(" last " + time_frame + " days of " + group);
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

	$( "#slider" ).slider( {min: 1, max: 30, step: 1,
		slide: function(event, ui) {
			if (ui.value == 1) {
				$("#time_display").html(" last " + ui.value + " day of " + group);
			} else {
				$("#time_display").html(" last " + ui.value + " days of " + group);
			}
			var status_url = "/group/" + group + "/status/" + ui.value +  "/json/";
			jQuery.get(status_url, function(data) {
				build_status_list(data);
			});
		}
	});

});

//fire this off on the page load
var ar_timer = window.setTimeout(check_requests, 10000);

// this will check every minute to see if there are any approvals to make 
function check_requests() {

	var requests_url = "/group/requests/" + user_name + "/json/";
	var html = "";
	jQuery.get(requests_url, function(data) {
		var data_length = data.length;
		if (data_length != 0) {
			html += "<h2>Group Requests</h2>";
			html += "<ul>";
		}
		for (var i = 0; i < data_length; i++) {
			html += "<li id=\"" + data[i].user_name + "\" >" + data[i].first_name + " " + data[i].last_name + "&nbsp;&nbsp; (" + data[i].group + ")";
			html += " &nbsp;&nbsp; ";
			html += "<a href=\"#\" user_id=\"" + data[i].id + "\" response=\"approve\" group=\"" + data[i].group + "\" class=\"requests button\">approve</a>";
			html += " or ";
			html += "<a href=\"#\" user_id=\"" + data[i].id + "\" response=\"deny\" group=\"" + data[i].group + "\" class=\"requests button\">deny</a>";
			html += "</li>"; 
		}
		html += "</ul>";
		$("#approve_requests").html(html).fadeIn('slow');
		jQuery(".requests").click(function() {
			var response_url = "/group/requests/" + user_name + "/json/";
			var response_data = {};
			response_data['user_id'] = jQuery(this).attr("user_id");
			response_data['response'] = jQuery(this).attr("response");
			response_data['group'] = jQuery(this).attr("group");
			jQuery.ajax({
				type: "POST",
				url: response_url,
				data: response_data,
				success: function(data) {
					var request_selector = "#" + data.user_name;
					jQuery(request_selector).html(data.user_feedback).fadeIn('slow');
				}
			});
				
		});
	});
	window.clearTimeout(ar_timer);
	
	ar_timer = window.setTimeout(check_requests, 20000);
}

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

/* will jackin the csf data on each POST */
$('html').ajaxSend(function(event, xhr, settings) {
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
        // Only send the token to relative URLs i.e. locally.
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
});
