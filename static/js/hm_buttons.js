return_button_func = function (name) {
    return function () {
        $.ajax({
            url: "/",
            type: 'POST',
            data: ({
                type: 'heatmap_button_event',
                current: window.current,
                pos: name,
                value0: window.value_heatmap0,
                value1: window.value_heatmap1,
                is_auto: window.is_heatmap_autoscale
            }),
            datatype: 'text',
            success: window.funcSucces
        })
    }
}

window.funcSucces = function (data) {
    window.current = data['current']
    $("#text_id").html(data['title'])
    $("#heatmap_graph").remove();
    $('<div>', {
        id: 'heatmap_graph'
    }).appendTo("#heatmaps")
    let graphs = JSON.parse(data['heatmap']);
    Plotly.plot('heatmap_graph', graphs, {});
}

window.firstSuccess = function (data) {

    let heatmap_graph = JSON.parse(data['heatmap']);
    let keogramm_graph = JSON.parse(data['keogram']);
    Plotly.plot('keogram_graph', keogramm_graph, {});
    Plotly.plot('heatmap_graph', heatmap_graph, {});

    let lightcurve_graph = JSON.parse(data['lightcurve']);
    Plotly.plot('lightcurve_graph', lightcurve_graph, {});


    lightcurve = document.getElementById('lightcurve_graph'),
        hoverInfo = document.getElementById('hoverInfo')

    lightcurve.on('plotly_click', function (data) {
        let x = data.points[0].x;
        $.ajax({
            url: "/",
            type: 'POST',
            data: ({
                type: 'lightcurve_click_event',
                x: x,
                value0: window.value_heatmap0,
                value1: window.value_heatmap1,
                is_auto: window.is_heatmap_autoscale
            }),
            datatype: 'text',
            success: window.funcSucces
        })
    })

    $("#next").trigger('click');

}

$(document).ready(function () {
    $("#next").bind("click", return_button_func('next'))
    $("#next2").bind("click", return_button_func('next2'))
    $("#next3").bind("click", return_button_func('next3'))
    $("#last").bind("click", return_button_func('last'))
    $("#last2").bind("click", return_button_func('last2'))
    $("#last3").bind("click", return_button_func('last3'))
})

window.is_heatmap_autoscale = false;