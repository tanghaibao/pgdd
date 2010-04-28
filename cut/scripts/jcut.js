
function example(t1, t2){
	$("#tree").val(t1);
	$("#list").val(t2);
}

// prepare the form when the DOM is ready 
$(function() { 
    var options = { 
        target:        '#display',   // target element(s) to be updated with server response 
        beforeSubmit:  showRequest,  // pre-submit callback 
        success: writeOutput
    }; 
 
    // bind form using 'ajaxForm' 
    $('#myform').ajaxForm(options); 
    $(':reset').click(function(){
        $("#display").html("");
    });
}); 
 
// pre-submit callback 
function showRequest(formData, jqForm, options) {
    $("#display").html("<img src='/duplication/images/loading.gif' />");
    return true; 
} 
 
// post-submit callback 
function showResponse(responseText, statusText)  { 
}
// success callback
function writeOutput(data) {
    $('#display').html(data);
}
