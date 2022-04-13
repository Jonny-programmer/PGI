$(document).ready(function() {
        $.ajax({
                url: "/",
                type: 'POST',
                data: ({
                    type: 'first_event',
                    first: true
                }),
                datatype: 'text',
                success: firstSuccess
            })
        window.value_heatmap0 = 20000
        window.value_heatmap1 = 200000

    })