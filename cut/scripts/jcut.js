
function example(t1, t2){
	$("#tree").val(t1);
	$("#list").val(t2);
}

// prepare the form when the DOM is ready 
$(function() { 
    var options = { 
        target:        '#display',   // target element(s) to be updated with server response 
        beforeSubmit:  showRequest,  // pre-submit callback 
        dataType: 'json',
        success: writeOutput
    }; 
 
    $('#discrete').button();
    $('#discrete').change( function(){
        if ($(this).attr("checked")) {
            $('#tinfo').html("treat values as discrete; use Fisher's exact test for significance testing");
        }
        else {
            $('#tinfo').html("treat values as continuous; use t-test for significance testing");
        }
    });

    // bind form using 'ajaxForm' 
    $('#myform').ajaxForm(options); 
    $(':reset').click(function(){
        $("#display").html("");
    });
}); 
 
// pre-submit callback 
function showRequest(formData, jqForm, options) {
    $("#display").html("<img src='/duplication/images/loading.gif' />");
    alert($.param(formData));
    return true; 
} 
 
// make result table
function makeResultTable(data) {
    var stdout_str = data.stdout_str;
    var res = "<tr class='hed'><td>Modules</td><td>Low/High</td><td>Mean value</td><td>P-value</td></tr>";
    for (var i=0; i<stdout_str.length; i++) {
        var fields = stdout_str[i].split("\t");
        var mrow = "";
        for (var j=0; j<fields.length; j++) {
            mrow += "<td>" + fields[j] + "</td>"
        }
        res += "<tr>" + mrow + "</tr>";
    }
    return "<table class='stats'>" + res + "</table>"
}

// success callback
function writeOutput(data) {
    var html_txt = "";
    html_txt += makeResultTable(data);
    // available debug information
    html_txt += "<a id='debug'>Debug</a><br />";
    html_txt += "<div id='dinfo' style='display: none'>";
    html_txt += "<b>Cmd</b>: " + data.cmd + "<br />";
    html_txt += "<b>Stderr</b>: <br />" + data.stderr_str.join("<br />") + "<br />";
    html_txt += "</div>"
    html_txt += "<img src='" + data.out_f + "' alt='' />";
    $('#display').html(html_txt);
    $('#debug').toggle(function(){$('#dinfo').show(); }, function(){$('#dinfo').hide(); });
}
