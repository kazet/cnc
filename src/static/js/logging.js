var logging = {};

logging.callAjaxAndLogErrors = function(url, parameters, errorLogger) {
    /*
     * A wrapper around jQuery.ajax that logs error responses using given error handler,
     * if any error happened, and then proceeds to execute callbacks provided by the caller.
    */

    var oldSuccessCallback = parameters.success;
    var oldErrorCallback = parameters.error;

    parameters.success = function(data) {
        if (data.status == "ERROR") {
            alert(data.message);
            errorLogger(data.message + '\n');
        } else {
            if (oldSuccessCallback !== undefined) {
                oldSuccessCallback(data);
            }
        }
    }

    parameters.error = function(xhr) {
        if (xhr.responseText) {
            errorLogger(xhr.responseText + '\n');
        }
        /* else: nothing interesting to display */

        if (oldErrorCallback !== undefined) {
            oldErrorCallback(data);
        }
    }

    $.ajax(url, parameters);
}
