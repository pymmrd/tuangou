$(function(){$("li a").click(function(){ var app = $(this).text(); var vcode = $(this).attr('name');var year = $("#year").val();var month = $("#month").val();var day = $("#day").val();var param = {'year': year, 'month': month, 'day':day, 'vcode': vcode};$.ajax({type: 'POST',url: '/commerce/ajax-show-app-click/',data: param,cache: true,dataType: 'json',success: function(response){$("#result").html(response.html); $("#strong").html(app);},});});})
