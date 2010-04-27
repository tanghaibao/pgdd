
function example(t1, t2){
	$("#nwk").val(t1);
	$("#csv").val(t2);
}
function reset(){
	$("#nwk").val("");
	$("#csv").val("");
	$("#display").html("");
}

function talktoServer(){
  	var url = "/duplication/cut/scripts/cut.py";
    var params = "";

	var tags = new Array("nwk","csv");
	for (var x=0; x<tags.length; x++)
	{
  		params += "&"+tags[x]+"="+escape($("#"+tags[x]).val());
	}

	$("#display").html("<img src='/duplication/images/loading.gif' />");
    var query = url+"?"+params;
	$.ajax({
		url: url,
		data: params,
		success: function(msg){
			$("#display").html(msg);
		},
        error: function(){
            $("#display").html("<font color='red'>Error in XmlHttpRequest: <a href='"+query+"'>"+query+"</a></font>");                                                  }
	});
}
