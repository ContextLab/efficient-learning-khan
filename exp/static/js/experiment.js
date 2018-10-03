var exptimeline = []
var recall_time = 1800 // 30 minutes
var predict_time = 300 // 5 minutes
var exit_time = 600 // 10 minutes

var runExperiment = function(options, conditions) {

  // instructions for 1st run
  var instructions = {
      type: "instructions",
      pages: ["<div class='instructions'> <p style='font-weight:bold'> PLEASE READ THESE INSTRUCTIONS CAREFULLY</p>" +
            "<p>In this experiment, you will <strong>watch</strong> a 20-25 minute episode of a TV show and <strong>recall</strong> what happened in as much detail as possible.</p>" +
            "<p>Press the spacebar to continue.</p></div>",
            "<div class='instructions'> <p> When the episode ends, you will see a red microphone icon (<i style='color:red' class='fa fa-microphone'></i>).  This indicates that the computer has started recording.</p>" +
            "<p>When you see the <i style='color:red' class='fa fa-microphone'></i>, <strong>recall</strong> the episode out loud as fully as you can.</p>" +
            "<p>Press the spacebar to continue.</p></div>",
            "<div class='instructions'> <p>Do your best to recount the events of the episode in order, using the characters' names and as much detail as you can remember, but if you realize you skipped something, feel free to go back and describe it.</p>" +
            "<p>Press the spacebar to continue.</p></div>",
            "<div class='instructions'> <p>You will have <strong>30 minutes</strong> to recall the episode, but if you feel you can't remember any more, you may stop after <strong>10 minutes</strong> by pressing the spacebar.</p>" +
            "<p>Press the spacebar to continue.</p></div>",
            "<div class='instructions'> <p>After that, you'll be asked to <strong>predict</strong> what you think will happen in the next episode.</p>" +
            "<p>When you see a blue microphone icon (<i style='color:blue' class='fa fa-microphone'></i>), you will have <strong>5 minutes</strong> to <strong>predict</strong> what will happen.</p>" +
            "<p>Press the spacebar to continue.</p></div>",
            "<div class='instructions'> <p>Okay that's everything! Ready to start?</p>" +
            "<p><strong>When you're ready to begin the episode, press the spacebar.</strong></p></div>"
          ],
      key_forward: 32
  };
  if (conditions.second_run==false) {exptimeline.push(instructions)};

  // instructions for 2nd run
  var returning_instructions = {
      type: "instructions",
      pages: ["<div class='instructions'> <p style='font-weight:bold'> PLEASE READ THESE INSTRUCTIONS CAREFULLY </p>" +
            "<p>In this experiment, you will start by <strong>recalling</strong> the episode you watched when you were last here.</p>" +
            "<p>When you see a green microphone icon (<i style='color:green' class='fa fa-microphone'></i>), <strong>recall</strong> the episode to the best of your ability.</p>" +
            "<p>Press the spacebar to continue.</p></div>",
            "<div class='instructions'> <p>You will have <strong>30 minutes</strong> to recall the episode, but if you feel you can't remember any more, you may stop after <strong>10 minutes</strong> by pressing the spacebar.</p>" +
            "<p>Press the spacebar to continue.</p></div>",
            "<div class='instructions'> <p>You will then <strong>watch</strong> a 20-25 minute episode of a TV show and <strong>recall</strong> what happened in as much detail as possible.</p>" +
            "<p>Press the spacebar to continue.</p></div>",
            "<div class='instructions'> <p> When the episode ends, you will see a red microphone icon (<i style='color:red' class='fa fa-microphone'></i>).</p>" +
            "<p>When you see the <i style='color:red' class='fa fa-microphone'></i>, <strong>recall</strong> the episode as fully as you can.</p>" +
            "<p> Press the spacebar to continue.</p></div>",
            "<div class='instructions'> <p>Do your best to recount the events of the episode in order, using the characters' names and as much detail as you can remember, but if you realize you skipped something, feel free to go back and describe it.</p>" +
            "<p>Press the spacebar to continue.</p></div>",
            "<div class='instructions'> <p>You will have <strong>30 minutes</strong> to recall the episode, but if you feel you can't remember any more, you may stop after <strong>10 minutes</strong> by pressing the spacebar.</p>" +
            "<p>Press the spacebar to continue.</p></div>",
            "<div class='instructions'> <p>Okay that's everything! Ready to start?</p>" +
            "<p><strong>When you're ready to recall the last episode, press the spacebar.</strong></p></div>"
          ],
      key_forward: 32
  };
  if (conditions.second_run) {exptimeline.push(returning_instructions)};

  // delayed recall instructions (2nd run only)
  var delayed_recall = {
        type: "free-recall",
        stimulus: "<p class='mic' style='position:absolute;top:31%;left:43%;font-size:20vw;color:green'><i class='fa fa-microphone blink_me' style='color:green'></i></p>",
        stim_duration: recall_time * 1000,
        trial_duration: recall_time * 1000 + 2000,
        record_audio: true,
        speech_recognition: 'google',
        recall_type: 'delayed',
        allow_exit_after: exit_time * 1000,
        data: {
          listNumber: 0
        },
        on_finish: function() {
            console.log('Saving delayed recall data...')
            psiTurk.saveData({
                success: function() {
                    console.log('Data saved!')
                }
            })
      }
  };
  if (conditions.second_run) {exptimeline.push(delayed_recall)};

  // pre-video instructions (2nd run only)
  var video_instructions = {
    type: "instructions",
    pages: ["<div class='instructions'><p>Thanks!</p>" +
    "<p><strong>When you're ready to watch the next episode, press the spacebar.</strong></p></div>"],
    key_forward: 32
  };
  if (conditions.second_run) {exptimeline.push(video_instructions)};

  // video
  var video = {
    type: "video",
    height: $(window).height(),
    width: $(window).width(),
    sources: [conditions.videostim],
  };
  exptimeline.push(video);

  // recall instructions
  var recall_instructions = {
      type: "instructions",
      pages: ["<div class='instructions'><p>When you see the <i style='color:red' class='fa fa-microphone'></i>, recall the episode to the best of your ability.</p>" +
              "<p>Please remember to speak <strong>clearly</strong>.</p>" +
              "<p><strong>When you're ready to begin recalling the episode, press the spacebar.</strong></p></div>"
            ],
      key_forward: 32
  };
  exptimeline.push(recall_instructions);

  // recall
  var recall = {
        type: "free-recall",
        stimulus: "<p class='mic' style='position:absolute;top:31%;left:43%;font-size:20vw;color:red'><i class='fa fa-microphone blink_me' style='color:red'></i></p>",
        stim_duration: recall_time * 1000,
        trial_duration: recall_time * 1000 + 2000,
        record_audio: true,
        speech_recognition: 'google',
        recall_type: 'recall',
        allow_exit_after: exit_time * 1000,
        data: {
          listNumber: 0
        },
        on_finish: function() {
            console.log('Saving recall data...')
            psiTurk.saveData({
                success: function() {
                    console.log('Data saved!')
                }
            })
      }
  };
  exptimeline.push(recall);

  // instructions for next episode prediction (1st run only)
  var predict_instructions = {
      type: "instructions",
      pages: ["<div class='instructions'><p>Now, when you see the <i style='color:blue' class='fa fa-microphone'></i>, predict what will happen in the next episode to the best of your ability.</p>" +
      "<p>Please remember to speak <strong>clearly</strong>.</p>" +
      "<p><strong>When you're ready to begin predicting, press the spacebar.</strong></p></div>"
      ],
      key_forward: 32
  };
  if (conditions.second_run==false) {exptimeline.push(predict_instructions)};

  // next episode prediction (1st run only)
  var predict = {
        type: "free-recall",
        stimulus: "<p class='mic' style='position:absolute;top:31%;left:43%;font-size:20vw;color:blue'><i class='fa fa-microphone blink_me' style='color:blue'></i></p>",
        stim_duration: predict_time * 1000,
        trial_duration: predict_time * 1000 + 2000,
        record_audio: true,
        speech_recognition: 'google',
        recall_type: 'prediction',
        data: {
          listNumber: 0
        },
        on_finish: function() {
            console.log('Saving prediction data...')
            psiTurk.saveData({
                success: function() {
                    console.log('Data saved!')
                }
            })
      }
  };
  if (conditions.second_run==false) {exptimeline.push(predict)};

  // finished message
  var finished_message = {
      type: "instructions",
      pages: ["<div class='instructions'><p>You're almost done!</p>" +
      "<p>Please go get your experimter.</p>" +
      "<p>Press the spacebar for the post-experiment questionnaire.</div>"],
      key_forward: 32
  };
  exptimeline.push(finished_message);

  // initialize
  jsPsych.init({
    timeline: exptimeline,
    on_finish: function() {
      psiTurk.recordTrialData(uniqueId),
      psiTurk.saveData({
        success: runPostQuestionnaire(options)
      })
    }
  })
};
