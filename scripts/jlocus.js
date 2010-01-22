$(function(){
    $("#lc").autocomplete("/duplication/scripts/autocomplete");
});

function example(locus){
	$("#lc").val(locus);
	talktoServer();
}
function reset(){
	$("#lc").val("");
    $("#sc2").attr("checked","checked");;
	$("#display").html("");
}

function talktoServer(){
  	var url = "/duplication/scripts/locus/locus1";
	var params = "lc="+$("#lc").val()+"&sc="+$("input[name=sc]:checked").val();
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
