$(function(){
	function get_height(){
		var ibody;
		if (document.documentElement && document.documentElement.scrollTop)
			ibody = document.documentElement.scrollTop;
		else if (document.body)
			ibody = document.body.scrollTop;
		else
			{/**/}
		var height;
		height = ibody + 150 + 'px';
		return height;
	}
	function get_width(){var width; width = document.body.scrollWidth; width = Math.ceil( width / 2 - 190 ) + "px"; return width;}
	$div = $("<div>");
	function creatediv($div){ var height = document.body.scrollHeight + "px"; var style = 'height:'+ height; $div.attr('style',style).addClass('lblack'); return $div;}
	function check_login(){
		var auth_key = $("#auth_key").val();
		if (!auth_key){
			creatediv($div);
			$("body").prepend($div);
			var showtop = 'top:'+ get_height() +';';
			var showleft = 'left:'+ get_width() +';';
			var showright = 'right:'+ get_width() +';';
			var showstyle = showtop + showleft + showright;
			$("#divlogin").attr('style', showstyle).show();
		};
	}
	$("#id_comment").focus(function(){check_login();});
	$("#wish_deal").click(function(){
		check_login();
		var wish_deal = $("#id_wish_deal").val();
		var param = {'wish_deal': wish_deal}
		$.ajax({
			type: 'POST',
			url : '/wishlist/add-wishlist/',
			data: param,
			cache: false,
			dataType: "json",
			success: function(response){
				alert(response.message);
			}
		});
	});
	$("#close_form").click(function(){$("#form_username").val(''); $("#form_password").val(''); $("#divlogin").attr('style', '').hide(); $("div.lblack").remove();});
	function set_cookies(key, value){str = document.cookies; str += key + '=' + value; document.cookies = str ;}
	function get_domain(){var protocol = location.protocol; var host  = location.host; var domain = protocol + '//' + host; return domain }
	$("#login_form").submit(function(){
		$.post('/accounts/signin-from-ajax/', $(this).serialize(), function(response){
			if (response.success == 'True'){
				$("#divlogin").attr('style', '').hide();
				$("div.lblack").remove();
				$("#auth_key").val(response.username);
				window.location.reload(); }else{ $("#divlogin").attr('style', '').hide(); var login_url = "/accounts/signin/?next=" + location.pathname; location.href = get_domain() + login_url;
			}
		}, 'json');
		return false;
	});
	$("#review_submit").click(function(){
		var content = $("#id_comment").val();
		var deal_id = $("#id_deal_id").val();
		var param ={'comment': content, 'deal_id':deal_id}; 
		$.ajax({
			type: 'POST',
			url: '/add-review/',
			data: param,
			cache: false,
			dataType: 'json',
			success: function(response){
				if (response.success == 'True'){
					$("div.hf").append(response.html);
					$("#id_comment").val('');
					var comment_num = parseInt($("#comment_num").text()) + 1;
					$("#comment_num").text(comment_num);
				}else{
					if (response.msg){
						alert(response.msg);
					}
				}
			}
		});
	});
	$('p.paginator a').live('click', function(){
		var page = $(this).attr('name');
		var deal_id = $("#id_deal_id").val();
		var param = {'page': page, 'deal_id':deal_id}; 
		$.get('/get-reviews/', param, function(response){
			if (response.success == 'True'){
				$("#reviews ~ div").remove();
				$("#reviews").after(response.html);
				$("p.paginator").html(response.page_html);
			}
		}, 'json');
	
	});
});
