$(function (){
	$("#ks_toggle").click(function(){
		$("#ks_dist").slideToggle("slow");
	});
});
function talktoServer(){
  	var url = "/duplication/scripts/dotplot/dotplot1";

	var params = "";

	var cb1 = ($("#cb1").attr("checked"))?1:0;
	var cb2 = ($("#cb2").attr("checked"))?1:0;
    var bp  = ($("#bp").attr("checked"))?1:0;
	params += "&ks_filter="+cb1+"&chr_filter="+cb2+"&bp="+bp;

	var tags = new Array("sp1","sp2","chr1","chr2","ks1","ks2");
	for (var x=0; x<tags.length; x++) {
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
            $("#display").html("<font color='red'>Error in XmlHttpRequest: <a href='"+query+"'>"+query+"</a></font>");                                                    }
	});
}

// chromosomal block 
function talktoServer_block(i,j){
  	var url = "/duplication/scripts/dotplot/dotplot1";

    if ($("#sp1").val()==$("#sp2").val() && i>j) {
        var k = i; i = j; j = k;
    }

	var params = "";

	var cb1 = ($("#cb1").attr("checked"))?1:0;
    var bp  = ($("#bp").attr("checked"))?1:0;
	params += "&ks_filter="+cb1+"&chr_filter=1"+"&chr1="+i+"&chr2="+j+"&block=1"+"&bp="+bp;

	var tags = new Array("sp1","sp2","ks1","ks2");
	for (var x=0; x<tags.length; x++) {
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
