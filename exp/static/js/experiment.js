var experimentTimeline = []

// video info
var vidstim1 = '/static/files/sample_video.mp4'
var vidstim2 = '/static/files/sample_video.mp4'

var runExperiment = function(options) {

  //fullscreen mode
  var fscreen = {
    type: 'fullscreen',
    message: '<p>We’d like you to really focus on this HIT so that we can collect clean data. Please turn off any music (but keep your volume turned on), close any additional open tabs in your browser (or any other open programs), remove any distractions around you (e.g. phone), and make yourself comfortable. When you are ready, please press the following button to switch your browser to fullscreen mode. (Your browser will remain in fullscreen for the duration of the HIT.  If you need to exit the HIT early, you may press ESCAPE (esc) to exit fullscreen mode and return your browser back to normal.</p>',
    button_label: 'Enter fullscreen mode',
    fullscreen_mode: true
   };

   experimentTimeline.push(fscreen)

  // opening instructions
  var open_instructions = {
      type: "instructions",
      pages: ["<div class='instructions'> <p style='font-weight:bold'> PLEASE READ THESE INSTRUCTIONS CAREFULLY</p>" +
            "<p>In this experiment, you will watch informational videos and answer questions about ______.</p>" +
            "<p>In total, you will be asked <strong>three</strong> sets of <strong>ten</strong> questions and you will watch <strong>two</strong> videos.</p>" +
            "<p>Press the spacebar to continue.</p></div>",
            "<div class='instructions'> <p>You will start the experiment by answering a set of ten questions about _____.</p>" +
            "<p>Even though you will not have watched an informational video yet, try to answer the questions to the best of your ability.</p>" +
            "<p>Press the spacebar to continue.</p></div>",
            "<div class='instructions'> <p>After you anwer the first set of questions, you will watch the informational videos and answer some more questions after each video.</p>" +
            "<p>Please, pay attention to the informational videos and try to learn about _____.</p>" +
            "<p>Then, try to use the knowledge you learned from the videos to answer the following questions.</p>" +
            "<p>Press the spacebar to continue.</p></div>",
            "<div class='instructions'> <p>Okay that's everything! Ready to start?</p>" +
            "<p><strong>When you're ready to begin the first set of questions, press the spacebar.</strong></p></div>"
          ],
      key_forward: 32
  };
  experimentTimeline.push(open_instructions);

  // test questions
  var test = {
      type: 'survey-multi-choice',
      questions: qset1,
        on_finish: function() {
            console.log('Saving recall data...')
            psiTurk.saveData({
                success: function() {
                    console.log('Data saved!')
                }
            })
      }
  };
  experimentTimeline.push(test);

  // instructions for first video
  var video1_instructions = {
      type: "instructions",
      pages: ["<div class='instructions'><p>You will now watch the first video.</p>" +
      "<p><strong>When you're ready to begin watching the first video, press the spacebar.</strong></p></div>"
      ],
      key_forward: 32
  };
  experimentTimeline.push(video1_instructions);

  // video
  var video = {
    type: "video",
    height: $(window).height(),
    width: $(window).width(),
    sources: [vidstim1],
  };
  experimentTimeline.push(video);

  // test instructions
  var test2_instructions = {
      type: "instructions",
      pages: ["<div class='instructions'><p>Now you will answer some questions about _____. Please, answer the questions to the best of your ability.</p>" +
              "<p><strong>When you're ready to begin answering the questions, press the spacebar.</strong></p></div>"
            ],
      key_forward: 32
  };
  experimentTimeline.push(test2_instructions);

  // test questions
  var test2 = {
      type: 'survey-multi-choice',
      questions: qset2,
        on_finish: function() {
            console.log('Saving recall data...')
            psiTurk.saveData({
                success: function() {
                    console.log('Data saved!')
                }
            })
      }
  };
  experimentTimeline.push(test2);

  // instructions for next video
  var video2_instructions = {
      type: "instructions",
      pages: ["<div class='instructions'><p>You will now watch the second video.</p>" +
      "<p><strong>When you're ready to begin watching the second video, press the spacebar.</strong></p></div>"
      ],
      key_forward: 32
  };
  experimentTimeline.push(video2_instructions);

  // video
  var video2 = {
    type: "video",
    height: $(window).height(),
    width: $(window).width(),
    sources: [vidstim2],
  };
  experimentTimeline.push(video2);

  // recall instructions
  var test3_instructions = {
      type: "instructions",
      pages: ["<div class='instructions'><p>Now you will answer some questions about _____. Please, answer the questions to the best of your ability.</p>" +
              "<p><strong>When you're ready to begin answering the questions, press the spacebar.</strong></p></div>"
            ],
      key_forward: 32
  };
  experimentTimeline.push(test3_instructions);

  // recall questions
  var test3 = {
      type: 'survey-multi-choice',
      questions: qset3,
        on_finish: function() {
            console.log('Saving recall data...')
            psiTurk.saveData({
                success: function() {
                    console.log('Data saved!')
                }
            })
      }
  };
  experimentTimeline.push(test3);


  // finished message
  var finished_message = {
      type: "instructions",
      pages: ["<div class='instructions'><p>You're almost done!</p>" +
      "<p>Please go get your experimter.</p>" +
      "<p>Press the spacebar for the post-experiment questionnaire.</div>"],
      key_forward: 32
  };
  experimentTimeline.push(finished_message);

  // initialize
//  jsPsych.init({
  //  timeline: experimentTimeline,
//    on_finish: function() {
//      psiTurk.recordTrialData(uniqueId),
//      psiTurk.saveData({
//        success: psiTurk.completeHIT()
//      })
//    }
//  })

  /*start experiment*/
  jsPsych.init({
    timeline: experimentTimeline,
    show_progress_bar: false,
    on_data_update: function(data) {
          psiTurk.recordTrialData(data)
            },
    on_finish: function() {
        console.log('Saving data...')

        //define functions to use below (modified from https://github.com/NYUCCL/psiTurk/blob/master/psiturk/example/static/js/task.js)
        var error_message = "<h1>Oops!</h1><p>Something went wrong submitting your HIT. This might happen if you lose your internet connection. Press the button to resubmit.</p><button id='resubmit'>Resubmit</button>";

        prompt_resubmit = function() {
          document.body.innerHTML = error_message;
          $("#resubmit").click(resubmit);
        }

        resubmit = function() {
          document.body.innerHTML = "<h1>Trying to resubmit...</h1>";
          reprompt = setTimeout(prompt_resubmit, 10000);
          psiTurk.saveData({
            success: function() {
                clearInterval(reprompt);
                        psiTurk.completeHIT() // when finished saving, compute bonus, then quit
            },
            error: prompt_resubmit //if error saving data, try again
          });
        };

          psiTurk.saveData({
              success: function() {
                  console.log('Data saved!')
                  psiTurk.completeHIT()
              },
              error: prompt_resubmit}) //if error saving data, try again
      //}
    },
});


};
