$(function(){
	$("#changelist-filter li a").click(function(){
		var year = $("#year").val();
		var month = $("#month").val();
		var day = $("#day").val();
		var page = $(this).parent().parent().attr('name');
		var area = $(this).attr('name');
		var param = {'year': year, 'month': month, 'day':day, 'page':page, 'area': area};
		$.ajax({
			type: 'POST',
			url : '/stats/get-area-audit/',
			data: param,
			cache: true,
			dataType: "json",
			success: function(response){$("#result").html(response.html)}
		});
	});
    $("h3.tips").click(function(){
		var year = $("#year").val();
		var month = $("#month").val();
		var day = $("#day").val();
        var page = $(this).next().attr('name');
        var param = {'year': year, 'month': month, 'day':day, 'page':page}
        $.ajax({
            type:"POST",
            url: '/stats/show-page-audit/', 
            data: param,
            cache: true,
            dataType:'json',
            success: function(response){$("#result").html(response.html)}
        });
    })
});
