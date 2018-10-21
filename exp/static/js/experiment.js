var exptimeline = []
var recall_time = 1800 // 30 minutes
var predict_time = 300 // 5 minutes
var exit_time = 600 // 10 minutes
var video1 = '/static/files/sample_video.mp4'
var video2 = '/static/files/sample_video.mp4'

var runExperiment = function(options) {

  //fullscreen mode
  var fscreen = {
    type: 'fullscreen',
    message: '<p>We’d like you to really focus on this HIT so that we can collect clean data. Please turn off any music (but keep your volume turned on), close any additional open tabs in your browser (or any other open programs), remove any distractions around you (e.g. phone), and make yourself comfortable. When you are ready, please press the following button to switch your browser to fullscreen mode. (Your browser will remain in fullscreen for the duration of the HIT.  If you need to exit the HIT early, you may press ESCAPE (esc) to exit fullscreen mode and return your browser back to normal.</p>',
    button_label: 'Enter fullscreen mode',
    fullscreen_mode: true
   };

   exptimeline.push(fscreen)

  // opening instructions
  var open_instructions = {
      type: "instructions",
      pages: ["<div class='instructions'> <p style='font-weight:bold'> PLEASE READ THESE INSTRUCTIONS CAREFULLY</p>" +
            "<p>In this experiment, you will <strong>watch</strong> two ___ minute Khan Academy video about the same topic and <strong>answer</strong> following questions about the topic covered in the videos.</p>" +
            "<p>Press the spacebar to continue.</p></div>",
            "<div class='instructions'> <p>Once the first video ends, answer the following questions to the best of your ability.</p>" +
            "<p>Press the spacebar to continue.</p></div>",
            "<div class='instructions'> <p>After you finish the first set of questions, you will watch the second video.</p>" +
            "<p>Press the spacebar to continue.</p></div>",
            "<div class='instructions'> <p>Once the second video ends, answer the following questions to the best of your ability.</p>" +
            "<p>Press the spacebar to continue.</p></div>",
            "<div class='instructions'> <p>Okay that's everything! Ready to start?</p>" +
            "<p><strong>When you're ready to begin the video, press the spacebar.</strong></p></div>"
          ],
      key_forward: 32
  };
  exptimeline.push(open_instructions);

  // video
  var video = {
    type: "video",
    height: $(window).height(),
    width: $(window).width(),
    sources: [video1],
  };
  exptimeline.push(video);

  // test instructions
  var test_instructions = {
      type: "instructions",
      pages: ["<div class='instructions'><p>When you see the <i style='color:red' class='fa fa-microphone'></i>, recall the episode to the best of your ability.</p>" +
              "<p>Please remember to speak <strong>clearly</strong>.</p>" +
              "<p><strong>When you're ready to begin recalling the episode, press the spacebar.</strong></p></div>"
            ],
      key_forward: 32
  };
  exptimeline.push(test_instructions);

  // test questions
  var test = {
      type: 'survey-multi-choice',
      questions: [
        {prompt: 'Question1?', options: ['A','B','C','D'], required: true},
        {prompt: 'Question2', options: ['A','B','C','D'], required: true}
      ],
        on_finish: function() {
            console.log('Saving recall data...')
            psiTurk.saveData({
                success: function() {
                    console.log('Data saved!')
                }
            })
      }
  };
  exptimeline.push(test);

  // instructions for next video
  var video2_instructions = {
      type: "instructions",
      pages: ["<div class='instructions'><p>Now, when you see the <i style='color:blue' class='fa fa-microphone'></i>, predict what will happen in the next episode to the best of your ability.</p>" +
      "<p>Please remember to speak <strong>clearly</strong>.</p>" +
      "<p><strong>When you're ready to begin predicting, press the spacebar.</strong></p></div>"
      ],
      key_forward: 32
  };
  exptimeline.push(video2_instructions);

  // video
  var video2 = {
    type: "video",
    height: $(window).height(),
    width: $(window).width(),
    sources: [video2],
  };
  exptimeline.push(video2);

  // recall instructions
  var test2_instructions = {
      type: "instructions",
      pages: ["<div class='instructions'><p>When you see the <i style='color:red' class='fa fa-microphone'></i>, recall the episode to the best of your ability.</p>" +
              "<p>Please remember to speak <strong>clearly</strong>.</p>" +
              "<p><strong>When you're ready to begin recalling the episode, press the spacebar.</strong></p></div>"
            ],
      key_forward: 32
  };
  exptimeline.push(test2_instructions);

  // recall questions
  var test2 = {
      type: 'survey-multi-choice',
      questions: [
        {prompt: 'Question1?', options: ['A','B','C','D'], required: true},
        {prompt: 'Question2', options: ['A','B','C','D'], required: true}
      ],
        on_finish: function() {
            console.log('Saving recall data...')
            psiTurk.saveData({
                success: function() {
                    console.log('Data saved!')
                }
            })
      }
  };
  exptimeline.push(test2);


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
