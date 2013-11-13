$(function(){
	function CharMode(iN) {
	if (iN>=48 && iN <=57) //数字
		return 1;
	if (iN>=65 && iN <=90) //大写字母
		return 2;
	if (iN>=97 && iN <=122) //小写
		return 4;
	else
		return 8; //特殊字符
	}
	//计算出当前密码当中一共有多少种模式
	function bitTotal(num) {modes=0; for (i=0;i<4;i++) {if (num & 1) modes++; num>>>=1;} return modes;}
	//返回密码的强度级别
	function checkStrong(sPW) {
	if (sPW.length<=4)
		return 0; //密码太短
		Modes=0;
		for (i=0;i<sPW.length;i++) {//测试每一个字符的类别并统计一共有多少种模式
		 Modes|=CharMode(sPW.charCodeAt(i));}
	   return bitTotal(Modes);
	}
	function pwStrength(pwd) {O_color="#eeeeee"; L_color="#FF0000"; M_color="#FF9900"; H_color="#33CC00"; if (pwd==null||pwd==''){ Lcolor=Mcolor=Hcolor=O_color;} else {
		S_level=checkStrong(pwd);
		switch(S_level) {
		case 0:
		 Lcolor=Mcolor=Hcolor=O_color;
		case 1:
		 Lcolor=L_color;
		 Mcolor=Hcolor=O_color;
		break;
		case 2:
		 Lcolor=Mcolor=M_color;
		 Hcolor=O_color;
		break;
		default:
		 Lcolor=Mcolor=Hcolor=H_color;
		}}
		document.getElementById("strength_L").style.background=Lcolor;
		document.getElementById("strength_M").style.background=Mcolor;
		document.getElementById("strength_H").style.background=Hcolor;
		return;
	}
	$("#password1").keyup(function(){var pwd = $(this).val(); pwStrength(pwd);}).blur(function(){ var pwd = $(this).val(); pwStrength(pwd);});
	var user_feed = '请用您的邮箱帐号注册';
	function check_fmt(value){
		var $this = $("#id_username");
		var feed = "请使用邮件地址";
		if (!value){$this.val(user_feed); return false;}
		if (value && value != user_feed){var emailRegExp = new RegExp("[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?");if (!emailRegExp.test(value) || value.indexOf('.') == -1){var $parent = $this.parent();$parent.append("<img class='tick' src='/static/images/safe-tips.gif'>"); $parent.append("<span class='highlight'>" + feed + "</span>"); return false;}}return true;}
	$("#id_nickname").blur(function(){ var nickname = $("#id_nickname").val(); var $parent = $(this).parent();
		if (nickname){var length = nickname.length; if (length > 20 || length <= 1){ if (length <=1){ var len_feed = '昵称长度过短';}else{ var len_feed = '不能超过20字节';}$parent.append("<img class='tick formtips' src='/static/images/safe-tips.gif'>");var $msg = $("<span class='highlight'>" + len_feed+ "</span>");$parent.append($msg);return false;}
		var param = {'nickname': nickname };
		$.ajax({type: 'POST', url : '/accounts/check-nickname/', data: param, cache:false, dataType: "json", success: function(response){
			if (response.success == 'True'){$parent.append("<img class='tick' src='/static/images/tick.gif'>");}else{ $parent.append("<img class='tick formtips' src='/static/images/safe-tips.gif'>"); var $msg = $("<span class='highlight'>" + response.msg + "</span>"); $parent.append($msg);}}})}
	}).focus(function(){$(this).siblings('.tick').remove();$(this).siblings('.highlight').remove();});
	$("#id_username").focus(function(){ if ($(this).val() == user_feed){$(this).val('');}  $(this).siblings('.tick').remove(); $(this).siblings('.highlight').remove();
	}).blur(function(){ var value = $(this).val(); var result = check_fmt(value); var $parent = $(this).parent()
		if (result){
			var param = {'username': value };
			$.ajax({type:'POST', url : '/accounts/check-username/', data: param, cache: false, dataType: "json", success: function(response){
			var $tick = $parent.find('.tick');
			if (response.success == 'True'){ if ($tick.length !=0){$tick.attr({'src': '/static/image/tick.gif'});}else{ $parent.append("<img class='tick' src='/static/images/tick.gif'>");}
					}else{ $parent.append("<img class='tick formtips' src='/static/images/safe-tips.gif'>"); var $msg = $("<span class='highlight'>" + response.msg + "</span>"); $parent.append($msg);}}});}});
});
