$(function(){$("a.delete").click(function(){var id = $(this).attr('title');var param = {'id': id};$.ajax({type:'POST', data: param,  url: '/union/site-pos-delete/', success:function(response){$("#item_"+id).remove(); alert('修改成功!');}, cache:false, dataType:'json'});});
  $("a.ad_delete").click(function(){var id = $(this).attr('title');var param = {'id': id};$.ajax({type:'POST', data: param,  url: '/union/delete-deal/', success:function(response){$("#item_"+id).remove(); alert('修改成功!');}, cache:false, dataType:'json'});});
  $(".checkbox").change(function(){if ($(this).is(":checked")){$(this).val('1');}else{$(this).val('0');}});
  $("#site").blur(function(){var site_id = $(this).val();var param = {'site_id': site_id};$next = $(this).next();$.ajax({type:'GET', data:param, url: '/union/get-site/', success: function(response){$tips = $('span.tips');if ($next.is("span.tips")){$tips.remove();}if (response.success == 'True'){$("#site").after("<span class='tips'>("+site_id + "/"+response.name+")</span>");}else{$("#site").after("<span class='tips'>"+response.msg+"</span>");}}, cache:false, dataType:'json'});}); $("tr:even").addClass('head');})
