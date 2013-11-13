$(function(){
	var feed = '修改成功';
	$("tr:odd").addClass('row1');
    $("select[name=category]").change(function(){
        var deal_id = $(this).attr('id');
        var category_id = $(this).val();
        var param = {'deal_id': deal_id, 'category_id':category_id}
        $.ajax({type: 'POST', url: '/classify/set-category/', data:param, cache:false, dataType:'json', success: function(response){if (response.success == 'True'){$(this).after("修改成功")}}});
    })  
})
