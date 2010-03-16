
function talktoServer(){
    var sp1 = $("#sp1").val();
    var sp2 = $("#sp2").val();
    if (sp1 && sp2 && sp1 > sp2) {
        var temp=sp1; sp1=sp2; sp2=temp;
    }

  	var url = "/duplication/scripts/download";
	var params = "sp1="+$("#sp1").val()+"&sp2="+$("#sp2").val();
	$("#display").html("<img src='/duplication/images/loading.gif' />");
    var query = url+"?"+params;
	$.ajax({
		url: url,
		data: params,
		success: function(msg){
			$("#display").html(msg);
            window.location.href = '/duplication/usr/'+sp1+'_'+sp2+'_block.csv.gz';
		},
        error: function(){
            $("#display").html("<font color='red'>Error in XmlHttpRequest: <a href='"+query+"'>"+query+"</a></font>");                                          }
	});
}
