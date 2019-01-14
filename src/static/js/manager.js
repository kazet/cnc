$(document).ready(function() {
    $('#manager-page').each(function() {
        function addToLogs(data) {
            $('textarea.logs').val($('textarea.logs').val() + data);
            $('textarea.logs').scrollTop($('textarea.logs')[0].scrollHeight);
        }

        function ajaxErrorLoggingCallWrapper(url, parameters) {
            var oldSuccessCallback = parameters.success;
            var oldErrorCallback = parameters.success;

            parameters.success = function(data) {
                if (data.status == "ERROR") {
                    alert(data.message);
                    addToLogs(data.message + '\n');
                } else {
                    if (oldSuccessCallback !== undefined) {
                        oldSuccessCallback(data);
                    }
                }
            }

            parameters.error = function(xhr) {
                if (xhr.responseText) {
                    addToLogs(xhr.responseText + '\n');
                }
                /* else: nothing interesting to display */

                if (oldErrorCallback !== undefined) {
                    oldErrorCallback(data);
                }
            }

            $.ajax(url, parameters);
        }

        var editor = ace.edit("editor");
        editor.setTheme("ace/theme/monokai");
        editor.session.setMode("ace/mode/python");

        $(this).find('.initialize-trigger').bind('click', function() {
            var button = $(this);

            ajaxErrorLoggingCallWrapper('/api/initialize/', {
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

            ajaxErrorLoggingCallWrapper('/api/pygcode/', {
                data: JSON.stringify({
                    'pygcode': 'emit("""G91 G00 X' + x + ' Y' + y + ' Z' + z + '""")'
                }),
                contentType: 'application/json',
                type: 'POST'
            });
        });

        $(this).find('.simulate').bind('click', function() {
            ajaxErrorLoggingCallWrapper('/api/simulate/json/', {
                data: JSON.stringify({
                    'pygcode': editor.getValue(),
                }),
                contentType: 'application/json',
                type: 'POST',
                success: function(data) {
                    initialize3dVisualization(
                        document.getElementById('simulation'),
                        data.moves,
                        parseFloat($('input.tool-diameter').val())
                    );
                },
            });
        });


        $(this).find('.run-pygcode').bind('click', function() {
            ajaxErrorLoggingCallWrapper('/api/pygcode/', {
                data: JSON.stringify({
                    'pygcode': editor.getValue(),
                }),
                contentType: 'application/json',
                type: 'POST',
            });
        });

        $(this).find('.abort').bind('click', function() {
            ajaxErrorLoggingCallWrapper('/api/abort/', {
                type: 'POST'
            });
        });

        setInterval(function() {
            ajaxErrorLoggingCallWrapper('/api/get_logs/', {
                type: 'POST',
                success: function(data) {
                    for (var i=0; i<data.logs.length; i++) {
                        if (data.logs[i].level == 'ERROR') {
                            alert(data.logs[i].message);
                        }

                        addToLogs(data.logs[i].message + '\n');
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
