var cnc_manager = {}


cnc_manager.initializeInitializeButton = function(button, loggingHandler) {
    /*
     * Initializes the "initialize" button behavior.
     */
    button.bind('click', function() {
        var button = $(this);

        logging.callAjaxAndLogErrors(
            '/api/initialize/',
            {
                type: 'POST',
                success: function(data) {
                    button.attr('disabled', true);
                    button.text('Machine initialized');
                }
            },
            loggingHandler
        );
    });
}


cnc_manager.initializeAbortButton = function(button, loggingHandler) {
    /*
     * Initializes the "abort" button behavior.
     */
    button.bind('click', function() {
        logging.callAjaxAndLogErrors(
            '/api/abort/',
            {
                type: 'POST'
            },
            loggingHandler
        );

        alert("The worker process has been killed. If you want to continue milling, restart the application.");
    });
}


cnc_manager.initializeMoveButtons = function(buttons, loggingHandler) {
    /*
     * Initializes the move buttons' behavior.
     */
    buttons.bind('click', function() {
        var scale = parseFloat($('input[name=move-scale]:checked').val());
        var x = parseFloat($(this).data('direction-x')) * scale;
        var y = parseFloat($(this).data('direction-y')) * scale;
        var z = parseFloat($(this).data('direction-z')) * scale;

        logging.callAjaxAndLogErrors(
            '/api/pygcode/',
            {
                data: JSON.stringify({
                    'pygcode': 'emit("""G91 G00 X' + x + ' Y' + y + ' Z' + z + '""")'
                }),
                contentType: 'application/json',
                type: 'POST'
            },
            loggingHandler
        );
    });
}

cnc_manager.initializeRunButton = function(button, editor, loggingHandler) {
    /*
     * Initializes the "run" button behavior.
     */
    button.bind('click', function() {
        logging.callAjaxAndLogErrors(
            '/api/pygcode/',
            {
                data: JSON.stringify({
                    'pygcode': editor.getValue(),
                }),
                contentType: 'application/json',
                type: 'POST',
            },
            loggingHandler
        );
    });
}


cnc_manager.initializeSimulateButton = function(button, editor, loggingHandler, visualizationContainer) {
    /*
     * Initializes the "simulate" button.
     */
    button.bind('click', function() {
        logging.callAjaxAndLogErrors(
            '/api/simulate/json/',
            {
                data: JSON.stringify({
                    'pygcode': editor.getValue(),
                }),
                contentType: 'application/json',
                type: 'POST',
                success: function(data) {
                    milling_3d_view.visualizeMoves(
                        visualizationContainer,
                        data.moves,
                        parseFloat($('input.tool-diameter').val())
                    );
                },
            },
            loggingHandler
        );
    });
}


cnc_manager.initializeEditor = function(editorId) {
    /*
     * Initialize the editor, given its DOM ID.
     */
    var editor = ace.edit(editorId);

    editor.setTheme("ace/theme/monokai");
    editor.session.setMode("ace/mode/python");

    return editor;
}


cnc_manager.initializePeriodicLogRead = function(loggingHandler) {
    /*
     * Initializes periodic API calls to the backend to obtain logs. The logs will then be passed to the handler.
     */
    setInterval(function() {
        logging.callAjaxAndLogErrors(
            '/api/get_logs/',
            {
                type: 'POST',
                success: function(data) {
                    for (var i=0; i<data.logs.length; i++) {
                        if (data.logs[i].level == 'ERROR') {
                            alert(data.logs[i].message);
                        }

                        loggingHandler(data.logs[i].message + '\n');
                    }
                }
            },
            loggingHandler
        );
    }, 500);
}


cnc_manager.initializeModulesList = function(container) {
    /*
     * Initialize the list of available modules.
     */
    container.find('.module').hide();
    container.find('.module-list a').bind('click', function() {
        container.find('.module').hide();
        container.find('.module[data-id=' + $(this).data('module-id') + ']').show();

        return false;
    });
}


cnc_manager.createLoggingHandler = function(container) {
    /*
     * Creates a logging handler, that displays logs in a textarea.
     */
    function loggingHandler(data) {
        container.find('textarea.logs').val($('textarea.logs').val() + data);
        container.find('textarea.logs').scrollTop($('textarea.logs')[0].scrollHeight);
    }

    return loggingHandler;
}


cnc_manager.initializeCNCManager = function(container) {
    /*
     * Initializes the behavior of the homepage main CNC manager.
     */

    var editor = cnc_manager.initializeEditor("editor");
    var loggingHandler = cnc_manager.createLoggingHandler(container);
    cnc_manager.initializeInitializeButton(container.find('.initialize-button'), loggingHandler);
    cnc_manager.initializeAbortButton(container.find('.abort-button'), loggingHandler);
    cnc_manager.initializeMoveButtons(container.find('.move-button'), loggingHandler);
    cnc_manager.initializeRunButton(container.find('.run-button'), editor, loggingHandler);
    cnc_manager.initializeSimulateButton(
        container.find('.simulate-button'),
        editor,
        loggingHandler,
        document.getElementById('simulation'),
    );
    cnc_manager.initializePeriodicLogRead(loggingHandler);
    cnc_manager.initializeModulesList(container);
}
