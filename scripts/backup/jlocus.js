
function example(locus){
	$("#lc").val(locus);
	talktoServer();
}
function reset(){
	$("#lc").val("");
	$("#display").html("");
}

function talktoServer(){
  	var url = "/duplication/scripts/locus/locus1";
	var params = "lc="+$("#lc").val();
	$("#display").html("<img src='/duplication/images/loading.gif' />");
	$.ajax({
		url: url,
		data: params,
		success: function(msg){
			$("#display").html(msg);
		},
		error: function(){
			$("#display").html("Error in XmlHttpRequest.");
		}
	});
}
