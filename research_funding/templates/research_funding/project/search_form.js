var resultsElement = $("#searchResults");
var searchInputElement = $("#searchInput")[0];

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

$("#searchInput").on("input", function(event) {
    $.ajax({
	url: "{% url 'project_search_results_json' %}",
	data: {
	    term: searchInputElement.value
	},
	success: function(result) {
	    var i, html = "";
	    html += "<ul class=\"list-group list-group-flush\">";
	    for (i=0; i<result.results.length; i++) {
		html += "<li class=\"list-group-item\">" +
		    highlight(result.results[i].title, result.term) +
		    "</li>";
	    }
	    html += "</ul>";
	    resultsElement.html(html);
	}
    });
});
