
$(function (){
	$("#ks_toggle").click(function(){
		$("#ks_dist").slideToggle("slow");
	});
});
function talktoServer(){
  	var url = "/duplication/scripts/dotplot/dotplot1";

 	var sp1 = $("#sp1").val();
 	var sp2 = $("#sp2").val();
	var params = "sp1="+sp1+"&sp2="+sp2;

	var cb1 = ($("#cb1").attr("checked"))?1:0;
	var cb2 = ($("#cb2").attr("checked"))?1:0;
	params += "&ks_filter="+cb1+"&chr_filter="+cb2;

	var tags = new Array("chr1","chr2","ks1","ks2");
	for (var x=0; x<tags.length; x++)
	{
  		params += "&"+tags[x]+"="+$("#"+tags[x]).val();
	}

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

// chromosomal block 
function talktoServer_block(i, j){
  	var url = "/duplication/scripts/dotplot/dotplot1";

 	var sp1 = $("#sp1").val();
 	var sp2 = $("#sp2").val();
	var params = "sp1="+sp1+"&sp2="+sp2;

	var cb1 = ($("#cb1").attr("checked"))?1:0;
	params += "&ks_filter="+cb1+"&chr_filter=1"+"&chr1="+i+"&chr2="+j;

	var tags = new Array("ks1","ks2");
	for (var x=0; x<tags.length; x++)
	{
  		params += "&"+tags[x]+"="+$("#"+tags[x]).val();
	}
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
