$(document).ready(function() {
    $("#comment").addEventListener('keydown', autosize);
    function autosize () {
        var el = this;
        setTimeout(function () {
            el.style.cssText = 'height:auto;';
            el.style.cssText = 'height:' + el.scrollHeight + 'px';
        }, 0);
    }
})