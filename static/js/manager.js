$(document).ready(function() {
    $('#page-manager').each(function() {
        $(this).find('.initialize-trigger').bind('click', function() {
            var button = $(this);

            $.ajax('/initialize/', {
                type: 'POST',
                success: function(data) {
                    button.attr('disabled', true);
                    button.text('Machine initialized');
                }
            });
        });

        $(this).find('.move-trigger').bind('click', function() {
            var scale = parseFloat($('input[name=move-scale]:checked').val());
            var x = parseFloat($(this).data('direction-x')) * scale;
            var y = parseFloat($(this).data('direction-y')) * scale;
            var z = parseFloat($(this).data('direction-z')) * scale;
            $.ajax('/gcode/', {
                data: JSON.stringify({
                    'gcode': 'G91 G00 X' + x + ' Y' + y + ' Z' + z
                }),
                contentType: 'application/json',
                type: 'POST',
            });
        });
        $(this).find('.run-gcode').bind('click', function() {
            $.ajax('/gcode/', {
                data: JSON.stringify({
                    'gcode': $('textarea.gcode').val(),
                }),
                contentType: 'application/json',
                type: 'POST',
            });
        });

        $(this).find('.abort').bind('click', function() {
            $.ajax('/abort/', {
                type: 'POST'
            });
        });

        setInterval(function() {
            $.ajax('/get_logs/', {
                type: 'POST',
                success: function(data) {
                    $('textarea.logs').val($('textarea.logs').val() + data);
                    $('textarea.logs').scrollTop($('textarea.logs')[0].scrollHeight);
                }
            });
        }, 500);
    });
});
