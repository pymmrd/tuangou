$(function(){
    function updateEndTime(){ 
        var date = new Date(); 
        var time = date.getTime(); 
        $(".settime").each(function(i){ 
            var d = this.getAttribute("endTime").split(',');
            var endDate = new Date(d[0], parseInt(d[1])-1, d[2], d[3], d[4], d[5]); 
            var endTime = endDate.getTime(); 
            var lag = (endTime - time) / 1000; 
            if(lag > 0){ 
                var second = Math.floor(lag % 60); 
                var minite = Math.floor((lag / 60) % 60); 
                var hour = Math.floor((lag / 3600) % 24); 
                var day = Math.floor((lag / 3600) / 24); 
                $(this).html(day+"天"+hour+"小时"+minite+"分"+second+"秒");
            }else{ 
                $(this).html("团购已经结束！");}});
            setTimeout(updateEndTime, 1000);
    }
    function update(){
        if($(".settime").length > 0){
        updateEndTime();}
    }
    update();
    var slug = $("span.on").attr('name');
    $("#"+slug).show();
    $(".nv_on span").mousemove(function(){
        $(this).addClass('on').siblings().removeClass('on');
        var slug = $(this).attr('name');
        $("#"+slug).show().siblings().hide();
    });
    $(".tm_r span").mouseover(function(){
        $(this).addClass('on').siblings().removeClass('on');
        var id = $(this).attr('name');
        $("#deal_"+id).show().siblings().hide();
    });
    $("div.tuan a").click(function(){
        var names = $(this).attr('name').split('_')
        var category = names[0];
        var position = names[1];
        var param = {'category': category, 'position': position};
        $.ajax({type:'POST', url:'/commerce/record-mini-click/', data: param, cache: false, datatType:'json'})
    });
});
