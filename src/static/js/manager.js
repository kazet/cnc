$(document).ready(function() {
    $('#manager-page').each(function() {
        function addToLogs(data) {
            $('textarea.logs').val($('textarea.logs').val() + data);
            $('textarea.logs').scrollTop($('textarea.logs')[0].scrollHeight);
        }

        var editor = ace.edit("editor");
        editor.setTheme("ace/theme/monokai");
        editor.session.setMode("ace/mode/python");

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
                    'gcode': 'emit("""G91 G00 X' + x + ' Y' + y + ' Z' + z + '""")'
                }),
                contentType: 'application/json',
                type: 'POST',
            });
        });

        $(this).find('.simulate').bind('click', function() {
            $.ajax('/simulate/', {
                data: JSON.stringify({
                    'gcode': editor.getValue(),
                }),
                contentType: 'application/json',
                type: 'POST',
                success: function(data) {
                    initialize3dVisualization(
                        document.getElementById('simulation'),
                        data,
                        parseFloat($('input.tool-diameter').val())
                    );
                },
                error: function(data) {
                    addToLogs(data.responseText + '\n');
                }
            });
        });


        $(this).find('.run-gcode').bind('click', function() {
            $.ajax('/gcode/', {
                data: JSON.stringify({
                    'gcode': editor.getValue(),
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
                    for (var i=0; i<data.length; i++) {
                        if (data[i].level == 'ERROR') {
                            alert(data[i].message);
                        }

                        addToLogs(data[i].message + '\n');
                    }
                }
            });
        }, 500);

        $('.module').hide();
        $(this).find('.module-list a').bind('click', function() {
            $('.module').hide();
            $('.module[data-id=' + $(this).data('module-id') + ']').show();

            return false;
        });
    });
});
