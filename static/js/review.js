$(function(){
    function get_height(){
        var ibody;
        if (document.documentElement && document.documentElement.scrollTop)
            ibody = document.documentElement.scrollTop;
        else if (document.body)
            ibody = document.body.scrollTop;
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
    function get_domain(){var protocol = location.protocol; var host  = location.host; var domain = protocol + '//' + host; return domain }
    $("#close_form").click(function(){$("#form_username").val(''); $("#form_password").val(''); $("#divlogin").attr('style', '').hide(); $("div.lblack").remove();});
    $("#login_form").submit(function(){
        $.post('/accounts/signin-from-ajax/', $(this).serialize(), function(response){
            if (response.success == 'True'){
                $("#divlogin").attr('style', '').hide();
                $("div.lblack").remove();
                $("#auth_key").val(response.username);
                window.location.reload();
            }else{
                $("#divlogin").attr('style', '').hide();
                var login_url = "/accounts/signin/?next=" + location.pathname;
                location.href = get_domain() + login_url;
            }   
        }, 'json');
        return false;
    }); 
    $("#review_submit").click(function(){
        var content = $("#id_comment").val();
        var deal_id = $("#id_deal_id").val();
        if (! content){ alert('评论不能为空!');}
        else{var param ={'comment': content, 'deal_id':deal_id}; 
        $.ajax({
                type: 'POST',
                url: '/commerce/review/',
                data: param,
                cache: false,
                dataType: 'json',
                success: function(response){
                    if (response.success == 'True'){
                        $("div.hf").append(response.html);
                        $("#id_comment").val('');
                        alert('评论成功！');
                    }
                }
            });
    }
    });
})

