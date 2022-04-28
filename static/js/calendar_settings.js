window.current_date = {'year': 0, 'month': 0, 'full_date': 0};

get_date_list = function (data) {
    console.log(data['data']);
    window.dates = data['data'].map(function (item, index, array) {
        return [parseInt(item[0]), parseInt(item[1]), parseInt(item[2])]
    });


    let new_dates = window.dates.map(function (item, index, array) {
        return new Date(item[2], item[1] - 1, item[0], 0, 0, 0).toString()
    });

    let dates_events = window.dates.map(function (item, index, array) {
        date = new Date(item[2], item[1] - 1, item[0], 0, 0, 0)
        return {
            startDate: date.toDateString(),
            endDate: date.toISOString(),
            summary: ''
        }
    });


    $(function () {
        $("#container").simpleCalendar();
    });

    let calendar = $("#container").simpleCalendar({

        // displays events
        displayEvent: true,

        // event dates
        events: dates_events,


        // disable showing event details
        disableEventDetails: false,

        // disable showing empty date details
        disableEmptyDetails: true,

        onMonthChange: function (month, year) {
            $(".today").removeClass("today");
            if (month == window.current_date['month'] && year == window.current_date['year'])
                date = window.current_date['full_date'];
            let a = $("div").find(`[data-date='${date}']`);
            a.addClass("today");
        },


        onDateSelect: function (date, events) {
            if (new_dates.indexOf(date.toString()) != -1) {

                year = parseInt(date.toISOString().split('-')[0])
                month = parseInt(date.toISOString().split('-')[1]) - 1
                full_date = date.toISOString()

                window.current_date = {'year': year, 'month': month, 'full_date': full_date};

                $(".today").removeClass("today");

                console.log(date.toDateString());
                console.log(date.toISOString());

                let a = $("div").find(`[data-date='${date.toISOString()}']`);
                a.addClass("today");


                $.ajax({
                    url: "/",
                    type: 'POST',
                    data: ({
                        type: 'date_event',
                        date: date.toDateString()
                    }),
                    datatype: 'text',
                    success: dateSuccess
                })


            }
        }


    });


    $(".today").removeClass("today");


}

$.ajax({
    url: "/",
    type: 'POST',
    data: ({
        type: 'get_date_list',
    }),
    datatype: 'text',
    success: get_date_list
})


// window.dates = [[23, 4, 2022], [25, 3, 2022], [20, 5, 2021], [2, 7, 2022], [4, 2, 2022], [13, 10, 2021]]


function dateSuccess(data) {

    $(".block").css("display", "block");
    $(".block1").css("display", "none");

    let top_pos = $(" #keogram_slider ").height() + $(" #keogram_slider ").position().top + $(" #autoscale_keogramm ").height();
    let left_pos = $(" #keogram_slider ").position().left - $(" #autoscale_keogramm ").width() * 2 / 3;
    $(" #autoscale_keogramm ").offset({top: top_pos, left: left_pos});

    let top_pos2 = $(" #heatmap_slider ").height() + $(" #heatmap_slider ").position().top + $(" #autoscale_heatmap ").height();
    let left_pos2 = $(" #heatmap_slider ").position().left - $(" #autoscale_heatmap ").width() * 2 / 3;
    $(" #autoscale_heatmap ").offset({top: top_pos2, left: left_pos2});

    $("#heatmap_graph").remove();
    $("#keogram_graph").remove();
    $("#lightcurve_graph").remove();

    $('<div>', {
        id: 'heatmap_graph'
    }).appendTo("#heatmaps");

    $('<div>', {
        id: 'keogram_graph'
    }).appendTo("#keogram");


    $('<div>', {
        id: 'lightcurve_graph'
    }).appendTo("#lightcurve");

    $("#heatmap_slider").slider("values", [20000, 200000]);
    $("#keogram_slider").slider("values", [20000, 200000]);

    window.change_pos(20000, " #first_keogram_text ", " #keogram_slider ");
    window.change_pos(200000, " #second_keogram_text ", " #keogram_slider ");
    window.change_pos(20000, " #first_heatmap_text ", " #heatmap_slider ");
    window.change_pos(200000, " #second_heatmap_text ", " #heatmap_slider ");

    window.current = -1;

    $.ajax({
        url: "/",
        type: 'POST',
        data: ({
            type: 'first_event',
            first: true
        }),
        datatype: 'text',
        success: window.firstSuccess
    })


}