/*
 * Example plugin template
 */

jsPsych.plugins["free-recall"] = (function() {

  var plugin = {};

  plugin.info = {
    name: "free-recall",
    parameters: {
      stimulus: {
            type: jsPsych.plugins.parameterType.HTML_STRING,
            default_value: "<p>stimulus</p>",
          },
      trial_duration: {
        type: jsPsych.plugins.parameterType.FLOAT, // BOOL, STRING, INT, FLOAT, FUNCTION, KEYCODE, SELECT, HTML_STRING, IMAGE, AUDIO, VIDEO, OBJECT, COMPLEX
        default: 60
      },
      stim_duration: {
        type: jsPsych.plugins.parameterType.FLOAT,
        default: 60
      },
      record_audio: {
        type: jsPsych.plugins.parameterType.BOOL,
        default: true
      },
      speech_recognizer: {
        type: jsPsych.plugins.parameterType.STRING,
        default: 'google'
      },
      recall_type: {
        type: jsPsych.plugins.parameterType.STRING,
        default: ''
      },
      allow_exit_after: {
        type: jsPsych.plugins.parameterType.FLOAT,
        default: 0
      }
    }
  }

  plugin.trial = function(display_element, trial) {

    var setTimeoutHandlers = [];

    display_element.innerHTML = trial.stimulus;

    // display_element.append($('<div>', {
    //   html: trial.stimulus,
    //   id: 'jspsych-free-recall-stimulus'
    // }));

    // hide image if timing is set
    if (trial.stim_duration > 0) {
      var t1 = setTimeout(function() {
        $('#jspsych-free-recall-stimulus').css('visibility', 'hidden');
      }, trial.stim_duration);
      setTimeoutHandlers.push(t1);
    }

    // end trial if time limit is set
    if (trial.trial_duration > 0) {
      var t2 = setTimeout(function() {
        mediaRecorder.stop();
      }, trial.trial_duration);
      setTimeoutHandlers.push(t2);
    };

    // end trial if minimum time is reached and key is pressed
    var endEarly = function(keypress) {
      if (keypress.rt > trial.allow_exit_after && trial.allow_exit_after != 0) {
        $('#jspsych-free-recall-stimulus').css('visibility', 'hidden');
        mediaRecorder.stop();
      }
    };

    var keyboardListener = jsPsych.pluginAPI.getKeyboardResponse({
      callback_function: endEarly,
      valid_responses: [' '],   // spacebar
      rt_method: 'date',
      persist: true
    });

    var mediaConstraints = {
      audio: true
    };

    navigator.getUserMedia(mediaConstraints, onMediaSuccess, onMediaError);

    function onMediaSuccess(stream) {
      mediaRecorder = new MediaStreamRecorder(stream);
      mediaRecorder.mimeType = 'audio/wav'; // audio/webm or audio/ogg or audio/wav
      mediaRecorder.audioChannels = 1;
      mediaRecorder.sampleRate = 44100;
      mediaRecorder.ondataavailable = function (blob) {
        var fileType = 'audio'; // or "audio"
        var fileName = uniqueId + '-' + trial.recall_type + '.wav';  // or "wav"

        var formData = new FormData();
        formData.append(fileType + '-filename', fileName);
        formData.append(fileType + '-foldername', uniqueId);
        formData.append(fileType + '-blob', blob);

        var request = new XMLHttpRequest();
        request.timeout = 120000; // time in milliseconds

        request.open("POST", "/save_audio");
        request.send(formData);

        display_element.append($('<div>', {
          html: "<p class='loading'><i class='fa fa-floppy-o blink_me'></i></p>"
        }));

        request.onreadystatechange = function() {
          if (request.readyState == XMLHttpRequest.DONE) {
            processAndFinishTrial(request.responseText);
          }
        }
      };
      mediaRecorder.start(99999999999)
      return mediaRecorder
    }

    function onMediaError(e) {
      console.error('media error', e);
    }

    function processAndFinishTrial(data){

      // kill any remaining setTimeout handlers
      for (var i = 0; i < setTimeoutHandlers.length; i++) {
        clearTimeout(setTimeoutHandlers[i]);
      }

      // kill keyboard listeners
      if (typeof keyboardListener !== 'undefined') {
        jsPsych.pluginAPI.cancelKeyboardResponse(keyboardListener);
      }

      // gather the data to store for the trial
      var trial_data = {
        "stimulus": trial.stimulus,
        "list_words": [],
        "recalled_words": trial.recalled_words,
      };

      jsPsych.data.write(trial_data);

      // clear the display
      // display_element.html('');
      display_element.innerHTML = ' ';

    // end trial
    jsPsych.finishTrial(trial_data);
    };
  }
  return plugin;
})();
