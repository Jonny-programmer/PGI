$(".ui-slider-vertical").slider({
    animate: 100,
    range: "min",
    min: 0,
    max: 500000,
    values: [20000, 200000],
    orientation: "vertical",
    step: 1
});

$("#heatmap_slider").slider({
    slide: function (event, ui) {
        window.change_pos(ui.values[0], " #first_heatmap_text ", " #heatmap_slider ");
        window.change_pos(ui.values[1], " #second_heatmap_text ", " #heatmap_slider ");
        console.log(ui)
    }
});

$("#heatmap_slider").slider({
    stop: function (event, ui) {
        window.value_heatmap0 = ui.values[0];
        window.value_heatmap1 = ui.values[1];

        heatmap = document.querySelector("#heatmap_graph>.js-plotly-plot");

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
        console.log(Plotly.relayout(heatmap, update));
    }
});
$(document).ready(function () {
    window.change_pos(20000, " #first_heatmap_text ", " #heatmap_slider ");
    window.change_pos(200000, " #second_heatmap_text ", " #heatmap_slider ");
    window.value_heatmap0 = 20000;
    window.value_heatmap1 = 200000;
})