// question info
var qset1 = [
  {prompt: 'Question1?', options: ['A','B','C','D'], required: true},
  {prompt: 'Question2?', options: ['A','B','C','D'], required: true},
  {prompt: 'Question3?', options: ['A','B','C','D'], required: true},
  {prompt: 'Question4?', options: ['A','B','C','D'], required: true},
  {prompt: 'Question5?', options: ['A','B','C','D'], required: true},
  {prompt: 'Question6?', options: ['A','B','C','D'], required: true},
  {prompt: 'Question7?', options: ['A','B','C','D'], required: true},
  {prompt: 'Question8?', options: ['A','B','C','D'], required: true},
  {prompt: 'Question9?', options: ['A','B','C','D'], required: true},
  {prompt: 'Question10?', options: ['A','B','C','D'], required: true}
]

var qset2 = [
  {prompt: 'Question1?', options: ['A','B','C','D'], required: true},
  {prompt: 'Question2?', options: ['A','B','C','D'], required: true},
  {prompt: 'Question3?', options: ['A','B','C','D'], required: true},
  {prompt: 'Question4?', options: ['A','B','C','D'], required: true},
  {prompt: 'Question5?', options: ['A','B','C','D'], required: true},
  {prompt: 'Question6?', options: ['A','B','C','D'], required: true},
  {prompt: 'Question7?', options: ['A','B','C','D'], required: true},
  {prompt: 'Question8?', options: ['A','B','C','D'], required: true},
  {prompt: 'Question9?', options: ['A','B','C','D'], required: true},
  {prompt: 'Question10?', options: ['A','B','C','D'], required: true}
]

var qset3 = [
  {prompt: 'Question1?', options: ['A','B','C','D'], required: true},
  {prompt: 'Question2?', options: ['A','B','C','D'], required: true},
  {prompt: 'Question3?', options: ['A','B','C','D'], required: true},
  {prompt: 'Question4?', options: ['A','B','C','D'], required: true},
  {prompt: 'Question5?', options: ['A','B','C','D'], required: true},
  {prompt: 'Question6?', options: ['A','B','C','D'], required: true},
  {prompt: 'Question7?', options: ['A','B','C','D'], required: true},
  {prompt: 'Question8?', options: ['A','B','C','D'], required: true},
  {prompt: 'Question9?', options: ['A','B','C','D'], required: true},
  {prompt: 'Question10?', options: ['A','B','C','D'], required: true}
  ]

var stimSelect = function(options){

  var rand_qset1 = jsPsych.randomization.repeat(qset1,1);
  var rand_qset2 = jsPsych.randomization.repeat(qset1,2);
  var rand_qset3 = jsPsych.randomization.repeat(qset1,3);

}
