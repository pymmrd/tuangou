lastScrollY = 0;
function heartBeat()
{ var ibody;
	var width;
	if (document.documentElement && document.documentElement.scrollTop){ ibody = document.documentElement.scrollTop; width = document.documentElement.scrollWidth;}
	else if (document.body){ ibody = document.body.scrollTop; width = document.body.scrollWidth;} else{/**/}
	var height;
	var iheight;
	height = document.documentElement.clientHeight;
	width = Math.ceil(width/2 + 502);
	iheight = Math.ceil((height-150)/10);
	if( lastScrollY > height){
		document.getElementById("goback").style.display = 'block';
	}else{
		document.getElementById("goback").style.display = 'none';
	}
	percent=.1*(ibody-lastScrollY); 
	if(percent>0)
		percent=Math.ceil(percent); 
	else
		percent=Math.floor(percent); 
	document.getElementById("goback").style.top = lastScrollY+"px";
	document.getElementById("goback").style.left = width+"px";
	lastScrollY=lastScrollY+percent+iheight;
}
// 执行
window.setInterval("heartBeat()",1);
