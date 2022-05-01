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

    $( ".list-group-item" ).remove();

    let heatmap_graph = JSON.parse(data['heatmap']);
    let keogramm_graph = JSON.parse(data['keogram']);
    Plotly.plot('keogram_graph', keogramm_graph, {});
    Plotly.plot('heatmap_graph', heatmap_graph, {});

    let lightcurve_graph = JSON.parse(data['lightcurve']);
    console.log(lightcurve_graph);
    let btn_list = ['zoom2d', 'pan2d', 'select2d', 'lasso2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d']
    Plotly.plot('lightcurve_graph', lightcurve_graph, {modeBarButtonsToRemove: ['toImage']});
    // fixme: modeBarButtonsToRemove do not work


    lightcurve = document.getElementById('lightcurve_graph')

    lightcurve.on('plotly_click', function (data) {
        let x = data.points[0].x;
        try {
            $('#timestamp').val(x);
        } catch (TypeError) {
            console.log('Okay, this happened again: x is now', typeof x)
        }
        ;
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

    let comments = data['comments'];

    console.log(comments);


    var format = function (str, col) {
        console.log(col)
        let values = ['profile_pic', 'name', 'surname', 'nickname', 'content', 'time_related', 'date_created'];
        let i = 0
        values.forEach(function (value) {
            console.log('{{ ' + value + ' }}')
            str = str.replace('{{ ' + value + ' }}', col[i]);
            i++;
        })
        return str;
    };

    comments.forEach(function (comment) {
        let text = `
            <li class="list-group-item list-group-item-info">
                <link rel="stylesheet" href="../../static/css/comment.css"/>
                <div class="comment-wrapper" align="center">
                    <div class="row">
                        <div class="col-2" align="content">
                            <img align="left" class="rounded-circle account-img" src="/static/img/profile_pics/${comment[0]}"/>
                        </div>
                        <div class="col-8" align="left">
                            <div class="row field-group">
                                <span style="float:left">
                                    <h3><b>${comment[1]} ${comment[2]}</b></h3>
                                </span>
                            </div>
                            <div class="row">
                                <h6>@${comment[3]}</h6>
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <p>${comment[4]}
                        </p>
                    </div>
                    <div class="field-group">
                        <span style="float:left">
                            <label class="date"><em>Time related - ${comment[5]}</em></label>
                        </span>
                        <span style="float:right">
                            <label class="date" ><em>Date created - ${comment[6]}</em></label>
                        </span>
                    </div>
                </div>
            </li>`
        $(' #comments ').append(text);
    })


}


window.lightcurveSucces = function (data) {
    console.log(data);

    $("#lightcurve_graph").remove();

    $('<div>', {
        id: 'lightcurve_graph'
    }).appendTo("#lightcurve");


    let lightcurve_graph = JSON.parse(data['lightcurve']);
    console.log(lightcurve_graph);
    Plotly.plot('lightcurve_graph', lightcurve_graph, {modeBarButtonsToRemove: ['toImage']});

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


$(document).ready(function () {
    $(" #form_submit ").bind("click", function () {
        console.log($("#timestamp").val())
        console.log($(' #comment_text ').val())
        console.log($(" #is_private ").val())
        if ($(' #comment_text ').val().length) {
            $.ajax({
                url: "/",
                type: 'POST',
                data: ({
                    type: 'new_comment_event',
                    timestamp: $("#timestamp").val(),
                    comment_text: $("#comment_text").val(),
                    is_private: $("#is_private").val()
                }),
                datatype: 'text',
                success: newCommentSuccess
            })
        }
    })

    let newCommentSuccess = function (data) {
        comment = data['comment']
        let text = `
            <li class="list-group-item list-group-item-info">
                <link rel="stylesheet" href="../../static/css/comment.css"/>
                <div class="comment-wrapper" align="center">
                    <div class="row">
                        <div class="col-2" align="content">
                            <img align="left" class="rounded-circle account-img" src="/static/img/profile_pics/${comment[0]}"/>
                        </div>
                        <div class="col-8" align="left">
                            <div class="row field-group">
                                <span style="float:left">
                                    <h3><b>${comment[1]} ${comment[2]}</b></h3>
                                </span>
                            </div>
                            <div class="row">
                                <h6>@${comment[3]}</h6>
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <p>${comment[4]}
                        </p>
                    </div>
                    <div class="field-group">
                        <span style="float:left">
                            <label class="date"><em>Time related - ${comment[5]}</em></label>
                        </span>
                        <span style="float:right">
                            <label class="date" ><em>Date created - ${comment[6]}</em></label>
                        </span>
                    </div>
                </div>
            </li>
            <br>`
        $(' #comments ').append(text);
    }

})