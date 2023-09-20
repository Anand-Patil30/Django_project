var player;
var video_list;
document.onreadystatechange = function () {
    if (document.readyState == "interactive") {
    player = document.getElementById("player");
    video_list = document.getElementById("video_list");
    maintainRatio();
    }
};
function maintainRatio() {
    var width = player.clientWidth;
    var height = (width * 9) / 16;
    console.log({ width, height });
    player.height = height;
    video_list.style.maxHeight=height+"px"

}
window.onresize = maintainRatio;

