$(function(){
    $.ajax({type: 'GET', url: '/accounts/get-login-box/', success: function(response){ $("#header").prepend(response.html); $("#auth_key").val(response.username)}, cache: false, dataType: 'json'});
    $("#logout").live('click', function(){$.get("/accounts/logout/",function(response){ if (response.success == 'True'){ $.ajax({type: 'GET', url: '/accounts/get-login-box/', success: function(response){ $("#header").prepend(response.html);}, cache: false, dataType: 'json'}); ;$(".header_top").html(response.html); var msg = "<p>登陆后才能使用收藏功能！点击<a class='login' href='javascript:void(0)'>登陆</a>或<a  class='close' href='javascript:void(0)'>关闭</a></p><span class='tixin_c'></span>";$("div.show_box").html(msg)}}, 'json'); $("#auth_key").val('');} );
	function updateEndTime(){var date = new Date();var time = date.getTime();$(".settime").each(function(i){ var d = this.getAttribute("endTime").split(',');var endDate = new Date(d[0], parseInt(d[1])-1, d[2], d[3], d[4],d[5]);var endTime = endDate.getTime();var lag = (endTime - time) / 1000;if(lag > 0){var second = Math.floor(lag % 60);var minite = Math.floor((lag / 60) % 60);var hour = Math.floor((lag / 3600) % 24);var day = Math.floor((lag / 3600) / 24); $(this).html(day+"天"+hour+"小时"+minite+"分"+second+"秒");}else{$(this).html("团购已经结束！");}});setTimeout(updateEndTime, 1000);}
	function update(){if($(".settime").length > 0){updateEndTime();}}
	update();
	function get_parent(obj){return obj.parent().parent()}
	$("a.reserve").click(function(){ var $this = $(this); var $bro = $this.parent().next(); if ($bro.is("div.reserve")){ $bro.show(); $this.hide().next().show();}else { var $parent = get_parent($this); var arr = $(this).attr('name').split('_'); var param = {'title': arr[0], 'index': arr[1]}; $.get('/get-reserve-deals/', param, function(response){ if(response.success == 'True'){ $parent.append(response.html); $this.hide().next().show(); update();}},'json')};})
	$("a.reserve_close").click(function(){  $(this).hide().siblings().show().parent().next().hide();});
	$("span.close").live('click', function(){ var $parent = get_parent($(this)).parent(); $parent.hide(); var $more = $parent.siblings('div.index_more');$more.children('a.reserve').show().end().children('a.reserve_close').hide();});
	$("div.c_city a").toggle(function(){var left = parseInt(document.body.clientWidth / 2 - 306 );$("#city_ul").attr('style', 'left:'+left+'px').show();}, function(){$("#city_ul").hide();})
	$(".tuan_box_mid dl").live('mouseover', function(){ $(this).attr('style', '');$(this).attr('class', 'tuan_box_hover'); $(this).children("span.sjss").show().end().children('div.bom').show();}).live('mouseout', function(){$(this).attr('class','tuan_box'); $(this).attr('style', 'position:absolute;z-index:0;');$(this).children("span.sjss").hide().end().children('div.bom').hide(); });
	$("#search_set :input").click(function(){var form_id = $(this).attr('title'); $("#"+form_id).show().siblings().hide();})
	function get_domain(){var protocol = location.protocol; var host  = location.host; var domain = protocol + '//' + host; return domain}
	$("#search_city_form").click(function(){ var name = $("#search_city_input").val(); if (name){var param = {'name': name}; $.ajax({ type: 'POST', url : '/search-city-form/', data: param,cache: false, dataType: "json", success: function(response){if (response.success == 'False'){$("#search_city_form").parent().append('<span class="highlight">'+ response.msg+"</span>");}else{var redirect_url = "/"+response.msg+"/"; 
    location.href = get_domain() + redirect_url;
    }}});}return false;});
    $("div.pc_d").mouseover(function(){$('div.idiv').show()}).mouseout(function(){$("div.idiv").hide()});
    function show_ul(name){$("#"+name).show().siblings().hide();$("."+name+"_hot").show().siblings(":gt(0)").hide();}
    var name = $("input[type=radio]:checked").val(); show_ul(name);
    $(".search_choice input[type=radio]").click(function(){var name = $(this).val();show_ul(name);});
    $("a.close").click(function(){$("div.show_box").hide();});
    $("a.wish").click(function(e){var left = e.pageX;var height = e.pageY;var id = $(this).parent().parent().attr('id');var auth_key = $("#auth_key").val();if (!auth_key){$("div.show_box").css({'left':left+'px', 'top':height+'px'}).show();}else{var param = {'wish_deal': id};$.ajax({type: 'POST',url : '/wishlist/add-wishlist/',data: param,cache: false,dataType: "json",success: function(response){$("div.show_box").css({'left':left+'px', 'top':height+'px'}).html(response.message).show().hide(10000);}});}});
});
