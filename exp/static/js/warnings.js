var runWarnings = function(options, cb) {
    if (options.show) {

        warningsTimeline = [];

        // instructions for microphone test
        var warnings1 = {
            type: 'text',
            text: "<div class='instructions'>" +
                "<p>For this experiment, we will be recording your voice while you recall lists of words, so you'll need to turn on your microphone. Please click <i>allow</i> when prompted. If your microphone is not working, you <b> will not be able to do this experiment.</b></p>" +
                "<p>Press any key to allow microphone access.</p></div>",
            is_html: true
        }
        warningsTimeline.push(warnings1);

        // create the mic test
        var micInit = {
            type: 'call-function',
            func: accessMic,
            timing_post_trial: 5000,
        };
        warningsTimeline.push(micInit);

        var warnings2 = {
            type: "text",
            text: "<div class= 'instructions'>" +
                "<p> For the duration of the experiment, you will need to remain in <strong>fullscreen mode</strong>. If this is not possible, please exit the experiment now.</p>" +
                "<p> Otherwise, please press a key to continue.</p></div>",
            html: true
        };
        warningsTimeline.push(warnings2);

        var warnings3 = {
            type: "text",
            text: "<div class= 'instructions'>" +
                "<p> Before we start, please make sure that your computer is connected to a <strong>power source</strong>.</p>" +
                "<p> Please do this now and then press any key to continue.</p></div>",
            html: true
        };
        warningsTimeline.push(warnings3);

        jsPsych.init({
            timeline: warningsTimeline,
            on_finish: function() {
                cb();
                psiTurk.saveData({
                    success: function() {
                        console.log("Warnings Shown!");
                    }
                });
            },
            on_data_update: function(data) {
                psiTurk.recordTrialData(data);
            }
        });
    } else {
        cb();
    };
};

var accessMic = function() {

    $spinner = "<div class='instructions'><p>Please click <strong>allow</strong>.</p></div>";
    $(".jspsych-display-element").append($spinner);

    //Wrap the getUserMedia function from the different browsers
    navigator.getUserMedia = navigator.getUserMedia ||
        navigator.webkitGetUserMedia ||
        navigator.mozGetUserMedia;

    //Our success callback where we get the media stream object and assign it to a video tag on the page
    function onSuccess(mediaObj) {
        window.stream = mediaObj;
        var video = document.querySelector("video");
        video.src = window.URL.createObjectURL(mediaObj);
        video.play();
    }

    //Our error callback where we will handle any issues
    function onError(errorObj) {
        console.log("There was an error: " + errorObj);
    }

    //We can select to request audio and video or just one of them
    var mediaConstraints = {
        video: false,
        audio: true
    };

    //Call our method to request the media object - this will trigger the browser to prompt a request.
    navigator.getUserMedia(mediaConstraints, onSuccess, onError);
};
