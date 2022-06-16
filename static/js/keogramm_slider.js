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
    $(id1).offset({top: value_top, left: value_left});
}

keogram_success = function (data) {
    $("#keogram_graph").remove();
    $('<div>', {
        id: 'keogram_graph'
    }).appendTo("#keogram")
    let graphs = JSON.parse(data);
    Plotly.plot('keogram_graph', graphs, {});
}


$("#keogram_slider").slider({
    slide: function (event, ui) {
        window.change_pos(ui.values[0], " #first_keogram_text ", " #keogram_slider ");
        window.change_pos(ui.values[1], " #second_keogram_text ", " #keogram_slider ");
    }
});

$("#keogram_slider").slider({
    stop: function (event, ui) {
        window.is_keogram_autoscale = false;
        window.value_keogram0 = ui.values[0];
        window.value_keogram1 = ui.values[1];
        $.ajax({
            url: "/",
            type: 'POST',
            data: ({
                type: 'keogram_slider_event',
                value0: ui.values[0],
                value1: ui.values[1],
            }),
            datatype: 'text',
            success: keogram_success
        })
    }
});

$(document).ready(function () {
    window.change_pos(20000, " #first_keogram_text ", " #keogram_slider ");
    window.change_pos(200000, " #second_keogram_text ", " #keogram_slider ");
    window.value_keogram0 = 20000;
    window.value_keogram1 = 200000;
})