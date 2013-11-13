<?php
    $one=$_POST["one"];
    $two=$_POST["two"];
    $three=$_POST["three"];
    $four=$_POST["four"];
    $five=$_POST["five"];
    $content=$_POST["content"];
    $userqq=$_POST["userqq"];
    date_default_timezone_set(PRC);
    $now_date=date("Y-m-d");    //当前日期
    $now_time=date("H:i:s");    //当前时间

    $usrip=$_SERVER['REMOTE_ADDR'];    //正在浏览当前页面用户的 IP 地址

    if($one==""){
        $one=0;
	}
	
    if($two==""){
        $two=0;
	}
	
    if($three==""){
        $three=0;
	}
	
    if($four==""){
        $four=0;
	}
	
    if($five==""){
        $five=0;
	}
	
    if($content==""){
        $content=0;
	}
	
    if($userqq==""){
        $userqq=0;
	}

    $sql_name = "uninstall";
    $id = mysql_connect("localhost","xiaoxia","admin4u");   // 登录数据库

    mysql_select_db($sql_name,$id);
    mysql_query("CREATE TABLE $sql_name (Num int(10) primary key auto_increment,bengkui varchar(10),gongneng varchar(10),jiemian varchar(10),queshao varchar(10),gengxin varchar(10),qq varchar(50),qita varchar(100),usrip varchar(20),now_date varchar(30),now_time varchar(30))",$id);   // 创建数据库列表
    mysql_query("SET CHARACTER SET utf8");   // 将数据库设置为简体中文

    $query="INSERT INTO $sql_name (bengkui,gongneng,jiemian,queshao,gengxin,qq,qita,usrip,now_date,now_time) VALUES ('$one','$two','$three','$four','$five','$userqq','$content','$usrip','$now_date','$now_time')";
    mysql_query($query,$id);
    mysql_close($id);
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>来点团-团购网|团购网站大全,最大的团购导航,北京团购网站大全,尽在来点团团购网!</title>
</head>
<body>
    <table width="320" border='0' cellspacing='1' cellpadding='1' bgcolor='#FFFFFF' align='center'>
      感谢您使用 来点团，您已成功卸载了。您的宝贵意见将帮助我们不断完善 来点团。我们会做得更好！
    </table>
</body>
</html>
