$(document).ready(function () {
    let nIntervId;

    function active() {

        if (!nIntervId) {
            nIntervId = setInterval(flashText, 100);
        }

        button_play = document.getElementById("play")
        if (button_play.title === "Stop") {
            clearInterval(nIntervId);
            nIntervId = null;
            button_play.title = "Play"
        } else {
            console.log("dfgfgfge")
            button_play.title = "Stop"
            console.log(button_play.title)
        }

        // check if already an interval has been set up

    }

    function flashText() {
        $.ajax({
            url: "/",
            type: 'POST',
            data: ({
                type: 'heatmap_button_event',
                current: window.current,
                pos: 'play',
                value0: window.value_heatmap0,
                value1: window.value_heatmap1,
                is_auto: window.is_heatmap_autoscale
            }),
            datatype: 'text',
            success: window.funcSucces
        })
    }


    document.getElementById("play").addEventListener("click", active);
})