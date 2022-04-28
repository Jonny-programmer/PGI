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
    console.log(lightcurve_graph);
    Plotly.plot('lightcurve_graph', lightcurve_graph, {});

    // var data2 = {
    //         x: [['2020-02-03T15:05:07']],
    //         y: [[20]]
    //     }
    //
    // Plotly.extendTraces("lightcurve_graph", data2, [0]);

    lightcurve = document.getElementById('lightcurve_graph')

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

    lightcurve.on('plotly_relayout',
        function (eventdata) {
            console.log(eventdata);
            if (eventdata['xaxis.autorange']) {
                $.ajax({
                    url: "/",
                    type: 'POST',
                    data: ({
                        type: 'lightcurve_all_graph_event'
                    }),
                    datatype: 'text',
                    success: window.lightcurveSucces
                });
            } else {
                x0 = eventdata['xaxis.range[0]'];
                x1 = eventdata['xaxis.range[1]'];
                y0 = eventdata['yaxis.range[0]'];
                y1 = eventdata['yaxis.range[1]'];

                $.ajax({
                    url: "/",
                    type: 'POST',
                    data: ({
                        type: 'lightcurve_change',
                        x0: x0,
                        x1: x1,
                        y0: y0,
                        y1: y1
                    }),
                    datatype: 'text',
                    success: window.lightcurveSucces
                });

            }
        })

    $("#next").trigger('click');

}


window.lightcurveSucces = function (data) {
    console.log(data);

    // var data = {
    //         x: [['2020-02-03T15:05:07', '2010-02-03T15:05:07']],
    //         y: [[20, 50]]
    //     }

    // Plotly.extendTraces("lightcurve_graph", data, [0]);

    $("#lightcurve_graph").remove();

    $('<div>', {
        id: 'lightcurve_graph'
    }).appendTo("#lightcurve");


    let lightcurve_graph = JSON.parse(data['lightcurve']);
    console.log(lightcurve_graph);
    Plotly.plot('lightcurve_graph', lightcurve_graph, {});

    lightcurve = document.getElementById('lightcurve_graph')

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

    lightcurve.on('plotly_relayout',
        function (eventdata) {
            console.log(eventdata);
            if (eventdata['xaxis.autorange']) {
                $.ajax({
                    url: "/",
                    type: 'POST',
                    data: ({
                        type: 'lightcurve_all_graph_event'
                    }),
                    datatype: 'text',
                    success: window.lightcurveSucces
                });
            } else {
                x0 = eventdata['xaxis.range[0]'];
                x1 = eventdata['xaxis.range[1]'];
                y0 = eventdata['yaxis.range[0]'];
                y1 = eventdata['yaxis.range[1]'];

                $.ajax({
                    url: "/",
                    type: 'POST',
                    data: ({
                        type: 'lightcurve_change',
                        x0: x0,
                        x1: x1,
                        y0: y0,
                        y1: y1
                    }),
                    datatype: 'text',
                    success: window.lightcurveSucces
                });

            }
        })


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