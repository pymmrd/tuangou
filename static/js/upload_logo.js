$(function(){
function showCoords(c){$("#imx1").val(c.x);$("#imy1").val(c.y); $("#imx2").val(c.x2); $("#imy2").val(c.y2);} 
$("#raw_image").Jcrop({onChange:showCoords, 
    onSelect: showCoords,
    minSize:[48, 48],
    aspectRatio: 1});
    });
