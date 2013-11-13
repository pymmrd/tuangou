$(function(){
    function add_record(param){
        $.ajax({type: 'POST',url : '/stats/add-pv-record/',data: param, cache: false, dataType: 'json'});
    }
    $("a.deal_link").live('click', function(){ 
        var id = $(this).attr('name'); 
        var $parent = $("#"+id); 
        var $hidden = $parent.children("input.hidden"); 
        var refer = $hidden.attr('name'); 
        var area = $hidden.val();
        var domain = $hidden.attr('title');
        var param = {'refer':refer, 'area':area, 'domain': domain, 'id': id};
        add_record(param);
        });
    $("div.today_show a").click(function(){
        var uri = $(this).attr('href').split('?');
        var url = uri[0].split('/');
        var id = url[url.length-2];
        var args = uri[1].split('&'); 
        var area = args[0].split('=')[1];
        var refer = args[1].split('=')[2];
        var domain = $(this).attr('name');
        var param = {'refer': refer, 'area': area, 'domain': domain, 'id': id};
        add_record(param);
    });
    $("a.count").live('click', function(){
        $.ajax({type:'GET', url: '/stats/add-click-counter/'})
    });
    
})
