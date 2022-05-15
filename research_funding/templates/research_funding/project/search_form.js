var resultsElement = $("#searchResults");
var searchInputElement = $("#searchInput")[0];
var programInputElement = $("#programInput")[0];
var managerInputElement = $("#managerInput")[0];

function highlight(s, term) {
    var tlen = term.length;
    if (tlen == 0) {
	return s;
    }
    var slow = s.toLowerCase();
    var tlow = term.toLowerCase();
    
    var indices = [];
    var idx = slow.indexOf(tlow);
    while (idx != -1) {
	indices.push(idx);
	idx = slow.indexOf(tlow, idx + tlen);
    }

    var result="", i;
    var lastIdx = 0;
    for (i=0; i<indices.length; i++) {
	result += s.slice(lastIdx, indices[i])
	result += "<span class=\"highlight\">" +
	    s.slice(indices[i], indices[i] + tlen) +
	    "</span>";
	lastIdx = indices[i] + tlen;
    }
    result += s.slice(lastIdx);
    
    return result;
}

function changeHandler(event) {
    program_and_department_name = programInputElement.value.split(",");
    program_name = program_and_department_name[0];
    department_name = program_and_department_name[1];
    $.ajax({
	url: "{% url 'project_search_results_json' %}",
	data: {
	    project_title: searchInputElement.value,
	    program_name: program_name,
	    department_name: department_name,
	    manager_id: managerInputElement.value
	},
	success: function(result) {
	    var i, html = "";
	    html += "<div class=\"d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom\">";
	    html += "<div class=\"table-responsive\">";
	    html += "<table class=\"table table-striped table-sm\">";
	    html += "<thead>";
	    html += "<th>Project title</th>";
	    html += "<th>Department name</th>";
	    html += "<th>Program name</th>";
	    html += "<th>Manager last name</th>";
	    html += "<th>Manager first name</th>";
	    html += "</thead>";
	    html += "<tbody>";
	    for (i=0; i<result.results.length; i++) {
		html += "<tr>" +
		    "<td>" + highlight(result.results[i].title, result.project_title_term) + "</td>" +
		    "<td>" + result.results[i].department_name + "</td>" +
		    "<td>" + result.results[i].program_name + "</td>" +
		    "<td>" + result.results[i].manager_last_name + "</td>" +
		    "<td>" + result.results[i].manager_first_name + "</td>" +
		    "</tr>";
	    }
	    html += "</tbody>";
	    html += "</table>";
	    html += "</div>";
	    html += "</div>";
	    resultsElement.html(html);
	}
    });
}

$("#searchInput").on("input", changeHandler);
$("#programInput").on("input", changeHandler);
$("#managerInput").on("input", changeHandler);

changeHandler();
