$(document).ready(function() {
    $('#page-manager').each(function() {
        function addToLogs(data) {
            $('textarea.logs').val($('textarea.logs').val() + data);
            $('textarea.logs').scrollTop($('textarea.logs')[0].scrollHeight);
        }

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

        $(this).find('.simulate').bind('click', function() {
            $.ajax('/simulate/', {
                data: JSON.stringify({
                    'gcode': $('textarea.gcode').val(),
                    'tool_diameter': $('input.tool-diameter').val(),
                }),
                contentType: 'application/json',
                type: 'POST',
                success: function(data) {
                    $('.simulation-image').html('');
                    img = $('<img />');
                    img.attr('src', '/' + data);
                    img.appendTo($('.simulation-image'));
                },
                error: function(data) {
                    addToLogs(data.responseText + '\n');
                }
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
                    addToLogs(data);
                }
            });
        }, 500);
    });
});
