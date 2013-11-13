linkTop = 0;
function topBack()
{
var ibody;
var iwidth;
var iright;

if(document.documentElement && document.documentElement.scrollTop){
ibody = document.documentElement.scrollTop;
iwidth = document.documentElement.scrollWidth;
iright = document.documentElement.scrollRight;
}else if (document.body){
ibody = document.body.scrollTop;
iwidth = document.body.scrollWidth;
iright = document.body.scrollRight;
}else{
/**/
}

iwidth = Math.ceil(iwidth/2 - 560);
//iright = Math.ceil(iright/2 + 560);

document.getElementById("topback").style.top = linkTop+"px";
document.getElementById("topback").style.left = iwidth+"px";
//document.getElementById("topback").style.right = iright+"px";
linkTop=ibody+190;
}
// 执行
window.setInterval("topBack()",1);
