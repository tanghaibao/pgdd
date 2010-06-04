
function example(seq){
	$("#seq").val(seq);
    talktoServer();
}
function reset(){
	$("#seq").val("");
	$("#display").html("");
}

function talktoServer(){
  	var url = "/duplication/scripts/blast/blast1";
    var params = "";

	var tags = new Array("seq","filter","evalue","program");
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
