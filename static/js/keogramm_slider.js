$(document).ready(function () {
    $("#autoscale_keogramm").bind("click",
        function () {

            keogram = document.getElementById("keogram_graph").querySelector(".js-plotly-plot");

            let update = {
                coloraxis: {
                    cmax: 0,
                    cmin: 0
                }
            }

            console.log(Plotly.relayout(keogram, update));
        });

    $("#autoscale_heatmap").bind("click", () => {
        window.is_heatmap_autoscale = true;
        let heatmap = document.querySelector("#heatmap_graph>.js-plotly-plot");

        let update = {
            coloraxis: {
                cmax: 0,
                cmin: 0
            }
        }

        console.log(Plotly.relayout(heatmap, update));
    });

});


$(".ui-slider-vertical").slider({
    animate: 100,
    range: "min",
    min: 20000,
    max: 500000,
    values: [20000, 200000],
    orientation: "vertical",
    step: 1
});


text_position = function (value, id) {
    let top_pos = $(id).height() * (1 - value / 500000);
    let left_pos = 2 * $(id).width();
    return [left_pos, top_pos]
}

window.change_pos = function (value, id1, id2) {
    $(id1).text(value / 1000 + 'K');
    value_left = text_position(value, id2)[0] + $(id2).position().left
    value_top = text_position(value, id2)[1] + $(id2).position().top - $(id1).height() / 2
    $(id1).offset({ top: value_top, left: value_left });
}

keogram_success = function (data) {
    $("#keogram_graph").remove();
    $('<div>', {
        id: 'keogram_graph'
    }).appendTo("#keogram")
    let graphs = JSON.parse(data);
    makeGraphPromise('keogram_graph', graphs)
}


$("#keogram_slider").slider({
    slide: function (event, ui) {
        window.change_pos(ui.values[0], " #first_keogram_text ", " #keogram_slider ");
        window.change_pos(ui.values[1], " #second_keogram_text ", " #keogram_slider ");
    }
});

$("#keogram_slider").slider({
    stop: function (event, ui) {
        window.value_keogram0 = ui.values[0];
        window.value_keogram1 = ui.values[1];

        keogram = document.querySelector("#keogram_graph>.js-plotly-plot");

        let max = (ui.values[0] > ui.values[1]) ? ui.values[0] : ui.values[1];
        let min = (ui.values[0] < ui.values[1]) ? ui.values[0] : ui.values[1];

        if (ui.values[0] == ui.values[1]) {
            min = 20000;
            max = 200000;
        }

        let update = {
            coloraxis: {
                cmax: max,
                cmin: min
            }
        }
        console.log(Plotly.relayout(keogram, update));

    }
});

$(document).ready(function () {
    window.change_pos(20000, " #first_keogram_text ", " #keogram_slider ");
    window.change_pos(200000, " #second_keogram_text ", " #keogram_slider ");
    window.value_keogram0 = 20000;
    window.value_keogram1 = 200000;
})