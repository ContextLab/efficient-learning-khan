var experimentTimeline = []

var debug = 0

if (debug){
  // debug video info
  var vidstim1 = '/static/files/sample_video.mp4'
  var vidstim2 = '/static/files/sample_video.mp4'
} else {
  // video info
  var vidstim1 = '/static/files/video1.mp4'
  var vidstim2 = '/static/files/video2.mp4'
}

// load question info
var qset1 = [
        {prompt: 'Why is the gravitational attraction between you and your computer too small for you to notice?',
        options: [ 'Neither you nor your computer has enough mass to cause a noticeable gravitational attraction',
       'You and your computer are too close for the gravitational attraction to be significant',
       'Humans are too small to detect the force of gravity'], required: true},
       {prompt: 'Which of the following is an example of the Weak Interaction?',
        options: [ 'A neutron in a radioactive Cesium atom is converted into a proton, leading to the release of a few particles',
       'Light from the sun collides with a satellite orbiting Earth and exerts a small push on the satellite',
       'Two protons bound together in a Helium nucleus resist separation despite a repulsive electromagnetic force acting on them'], required: true},
       {prompt: 'Roughly how many times stronger is the Weak Interaction than gravity?',
        options: [ '10,000,000,000,0 00,000',
       '10',
       '1,000,000'], required: true},
       {prompt: 'Why don’t you and your computer experience any attraction or repulsion due to the Weak Interaction?',
        options: [ 'The weak interaction only acts over extremely small distances',
       'The weak interaction between you and your computer is counteracted by the other forces',
       'You and your computer have no net charge'], required: true},
       {prompt: 'Which of the following is a difference between gravity and the electromagnetic force?',
        options: [ 'Gravity is only ever attractive while the electromagnetic force can both attract and repel',
       'Gravity is a much more powerful force than electromagnetis m',
       'Gravity can only act over large distances while the electromagnetic force can act over large and small distances'], required: true},
       {prompt: 'Electricity and magnetism can be shown to be two cases of the same force if we:',
        options: [ 'View them in different frames of reference',
       'Switch which charges we call positive and which charges we call negative',
       'Consider both the effects over small distances and the effects over large distances'], required: true},
       {prompt: 'Which of the following are the primary two fundamental forces acting in opposition between the positively-charged protons in an atom’s nucleus?',
        options: [ 'The Strong Force and the Electromagnetic Force',
       'Gravity and the Weak Interaction',
       'Gravity and the Electromagnetic Force'], required: true},
       {prompt: 'Why does the universe have a very uneven distribution of mass but a relatively equal distribution of charge?',
        options: [ 'Positive and negative charges cancel out and become a neutral charge when they combine while masses only grow larger as they combine',
       'Masses tend to repel while charges tend to attract',
       'Masses tend to attract while charges tend to repel'], required: true},
       {prompt: 'In your body, there are a tremendous amount of negatively-charged electrons. Your computer also contains a huge number of negatively-charged electrons. We know that like charges repel, but you and your computer are not repelled apart. Which of the following explains why?',
        options: [ 'The electrons’ negative charges are balanced by the positive charges of an equal number of protons',
       'An attractive gravitational force balances out this repulsion',
       'The Electromagnetic force only acts over very small distances'], required: true},
       {prompt: 'Which of the following is a similarity between the Weak Interaction and the Strong Force?',
        options: [ 'Both act only over very small distances',
       'Both are stronger than the Electromagnetic force',
       'Both are weaker than Gravity'], required: true},
       {prompt: 'Which force is stronger than the Electromagnetic Force?',
        options: [ 'Strong Force',
       'Gravity',
       'Weak Interaction'], required: true},
       {prompt: 'Roughly how many times stronger is the Strong Force than gravity?',
        options: [ '10ˆ38',
       '100',
       '10ˆ18'], required: true},
       {prompt: 'Which of the following would have to be true for the Weak Interaction to cause repulsion or attraction between two objects?',
        options: [ 'The objects would have to be extremely close to each other',
       'The objects would have to have the same mass',
       'The objects would have to be extremely far away from each other'], required: true},
       {prompt: 'Which force keeps us from jumping off of Earth?',
        options: [ 'Gravity',
       'Strong Force',
       'Weak Interaction'], required: true},
       {prompt: 'What does the Coulomb Force refer to?',
        options: [ 'The repulsion of objects with similar charge and the attraction of objects with different charge',
       'The repulsion of objects with similar mass and the attraction of objects with different mass',
       'The repulsion of objects with similar temperature and the attraction of objects with different temperature'], required: true},
       {prompt: 'Which fundamental force is responsible for holding the nucleus of an atom together?',
        options: [ 'Strong Force',
       'Gravity',
       'Electromagnetic force'], required: true},
       {prompt: 'How does the electromagnetic force differ from the strong and weak nuclear forces?',
        options: [ 'Electromagnetic force is a long-range force, while strong and weak nuclear forces are short-range forces.',
       'The electromagnetic force is much weaker than the strong and weak nuclear forces.',
       'The electromagnetic force only affects particles that have an electric charge, while the strong and weak nuclear forces can affect any particle.'], required: true},
       {prompt: 'Which of the following particles is not affected by the electromagnetic force?',
        options: [ 'Neutron',
       'Proton',
       'Electron'], required: true},
       {prompt: 'Which of the following forces is most influential at the largest scales of the universe?',
        options: [ 'Gravitational force',
       'Electromagnetic force',
       'Strong force'], required: true},
       {prompt: 'Which of the following is true about gravity?',
        options: [ 'It is the weakest fundamental force.',
       'It is the strongest fundamental force.',
       'It is only noticeable on the molecular scale.'], required: true},
       {prompt: 'Which of the following is an example of beta minus decay?',
        options: [ 'A neutron turns into a proton.',
       'A proton turns into a neutron.',
       'An electron turns into a proton.'], required: true},
       {prompt: 'How does the strength of the electromagnetic force compare to the strength of the weak force?',
        options: [ 'It is 10^12 times stronger',
       'It is about the same',
       'It is 10 times weaker'], required: true},
       {prompt: 'Why do two protons in a nucleus not repel each other due to the Coulomb force?',
        options: [ 'Because there is a stronger force than the Coulomb force that keeps them together',
       'Because they have opposite charges',
       'Because there are electrons around the nucleus that attract them'], required: true},
       {prompt: 'Your friend suggests that the electromagnetic force keeps Saturn in orbit around the sun. Why is she incorrect?',
        options: [ 'The gravitational force keeps saturn in orbit around the sun',
       'The weak interactions keeps saturn in orbit around the sun',
       'The strong force keeps saturn in orbit around the sun'], required: true},
       {prompt: 'For what reason might your chemistry course not discuss gravity on the subatomic level?',
        options: [ 'The other forces completely dominate interactions on subatomic levels',
       'Gravity does not exist at a subatomic level',
       'Your professor mistakenly neglected this significant topic'], required: true},
       {prompt: 'The term “nucleons” does not include:',
        options: [ 'Electrons',
       'Protons',
       'Neutrons'], required: true},
       {prompt: 'Why doesn’t the weak interaction operate between the planets in our solar system?',
        options: [ 'Because it only applies to very small distances',
       'Because it is the weakest fundamental force',
       'Because objects with large mass are immune to the weak interaction'], required: true},
       {prompt: 'What is the significance of concentration of mass in regards to the fundamental forces?',
        options: [ 'It allows gravitational force to operate over macro scales',
       'It allows electromagnetic force to operate over macro scales',
       'It allows gravitational force to operate over micro scales'], required: true},
       {prompt: 'Without the strong force, what would hypothetically happen to the subatomic particles in the nucleus of an atom?',
        options: [ 'Like charges would repel each other due to the Coulomb force',
       'Like charges would continue to be situated right next to each other due to the Coulomb force',
       'Like charges would continue to be situated right next to each other due to the gravitational force'], required: true},
       {prompt: 'What do the gravitational force and electromagnetic force have in common?',
        options: [ 'They are both weaker than the strong force',
       'They both operate over very large distances',
       'They are both stronger than the weak interaction'], required: true}]       

var qset2 = [
        {prompt: 'Which of the following describes the effect of gravity on a cloud of atoms',
        options: [ 'The atoms move to the center of the mass of the atoms',
       'The atoms move away from the center of the mass of the atoms',
       'The atoms spin around the center of the mass of the atoms'], required: true},
       {prompt: 'Which of the following occurs as a cloud of atoms gets more dense?',
        options: [ 'Temperature increases',
       'Temperature decreases',
       'Mass increases'], required: true},
       {prompt: 'Which temperature does a cloud of hydrogen atoms approach as it gets denser in the process of becoming a star',
        options: [ '10 million Kelvin',
       '0 Kelvin',
       '10,000 Kelvin'], required: true},
       {prompt: 'Which of the following can overcome the Coulomb Force?',
        options: [ 'High temperature and high pressure',
       'Low temperature and high pressure',
       'High temperature and low pressure'], required: true},
       {prompt: 'Which of the following prevents a star from collapsing as a result of gravity?',
        options: [ 'Energy released from the fusion of the hydrogen atoms provides outward pressure',
       'The fusion of hydrogen atoms decreases the temperature of the star',
       'The gravitational pull of other stars nearby'], required: true},
       {prompt: 'How are supermassive stars different from other stars?',
        options: [ 'Fusion occurs very fast',
       'Fusion occurs very slow',
       'Fusion occurs in the reverse order'], required: true},
       {prompt: 'Which of the following is the FIRST product of two hydrogen atoms fusing together?',
        options: [ 'Deuterium',
       'Oxygen',
       'Helium'], required: true},
       {prompt: 'Once hydrogen atoms get close enough together, which of the following keeps them together?',
        options: [ 'The Strong Force',
       'The Electromagnetic Force',
       'Gravity'], required: true},
       {prompt: 'When two nuclei fuse together, how does the mass of the combined nucleus compare to the mass of each of the original nucleus?',
        options: [ 'The mass of the combined nucleus is smaller',
       'The mass of the combined nucleus is larger',
       'The mass of the combined nucleus is the same'], required: true},
       {prompt: 'If we say that our Sun is a main sequence star, what does that tell us about the Sun?',
        options: [ 'Hydrogen atoms in the Sun are fusing together and becoming Helium',
       'The Sun is a supermassive star',
       'The Sun does not experience the force of Gravity but does experience the Coulomb Force'], required: true},
       {prompt: 'Which force would cause a massive cloud of hydrogen atoms to move together?',
        options: [ 'Gravity',
       'Strong Force',
       'Weak Interaction'], required: true},
       {prompt: 'Which of the following occurs as density increases?',
        options: [ 'Temperature increases',
       'Volume increases',
       'Mass increases'], required: true},
       {prompt: 'Which of the following is a product of Hydrogen fusion?',
        options: [ 'Helium',
       'Oxygen',
       'Cesium'], required: true},
       {prompt: 'Which of the following terms accurately describes the Sun?',
        options: [ 'Main sequence star',
       'Supermassive star',
       'Alternative sequence star'], required: true},
       {prompt: 'Which of the following terms best describes a fusion reaction?',
        options: [ 'Ignition',
       'Combustion',
       'Decomposition'], required: true},
       {prompt: 'What happens to the Coulomb force when the two nucleuses get close enough to each other?',
        options: [ 'It becomes weaker',
       'It becomes stronger',
       'It disappears'], required: true},
       {prompt: 'What happens when two hydrogen nuclei fuse together?',
        options: [ 'They degrade into neutrons',
       'They degrade into electrons',
       'They degrade into protons'], required: true},
       {prompt: 'What is the resulting energy of the fusion reaction?',
        options: [ 'Positive energy',
       'Negative energy',
       'No energy'], required: true},
       {prompt: 'What does the energy from the fusion reaction provide for the star?',
        options: [ 'Outward pressure',
       'Inward pressure',
       'No pressure'], required: true},
       {prompt: 'What, most specifically, defines fusion ignition?',
        options: [ 'The fusion of two hydrogen nuclei to form helium',
       'The combustion of hydrogen and oxygen',
       'The release of energy from the Sun'], required: true},
       {prompt: 'What is deuterium?',
        options: [ 'A form of heavy hydrogen with one neutron and one proton',
       'Another name for helium',
       'A molecule made up of two hydrogen atoms'], required: true},
       {prompt: 'What happens to the cloud as it gets denser and denser?',
        options: [ 'The hydrogen atoms start to interact with each other',
       'The hydrogen atoms begin to repel each other',
       'The helium atoms start to interact with each other.'], required: true},
       {prompt: 'Why is the energy released during fusion greater than the mass difference between the reactants and products?',
        options: [ 'Because of the conversion of mass to energy',
       'Because of the conversion of protons to neutrons',
       'Because of the conversion of neutrons to protons'], required: true},
       {prompt: 'If a cloud of hydrogen atoms were to expand, which of the following would occur?',
        options: [ 'None of the above',
       'Interactions between atoms would increase',
       'Density of the atoms would increase'], required: true},
       {prompt: 'What is required to draw together the positive nuclei of 2 atoms?',
        options: [ 'Huge pressures',
       'Low temperatures',
       'The Coulomb Force'], required: true},
       {prompt: 'What provides the pressure for fusion ignition once the star is created?',
        options: [ 'External molecules trying to get in',
       'Increasing volume of the nucleus',
       'Decreasing temperature of the hydrogen molecules'], required: true},
       {prompt: 'Why is deuterium nicknamed “heavy hydrogen”',
        options: [ 'It has had an additional neutron',
       'It has an additional electron',
       'It has an additional proton'], required: true},
       {prompt: 'Which of the following lists the reactions in star formation in the correct order?',
        options: [ 'Hydrogen to deuterium to helium',
       'Hydrogen to helium to deuterium',
       'Helium to deuterium to hydrogen'], required: true},
       {prompt: 'Which of the following has the most protons',
        options: [ 'Helium',
       'Hydrogen',
       'Deuterium'], required: true},
       {prompt: 'Why does the formation of Helium-4 release energy?',
        options: [ 'Mass is reduced',
       'Mass is increased',
       'Velocity is reduced'], required: true}
       ]

var qset3 = [
        {prompt: 'Which of the following lists of particles is ordered from smallest to largest?',
        options: [ 'Electron, proton, nucleus, atom',
       'Atom, electron, proton, nucleus',
       'Atom, electron, proton, nucleus'], required: true},
       {prompt: 'Which of the following defines what element an atom is?',
        options: [ 'Its number of protons',
       'Its number of neutrons',
       'Its number of electrons'], required: true},
       {prompt: 'Suppose that in some atom, a proton is converted into a neutron. What changes as a result of this conversion?',
        options: [ 'The atom’s element',
       'The atom’s mass (in atomic mass units)',
       'The atom’s velocity'], required: true},
       {prompt: 'Which of the following lists is ordered from smallest to largest?',
        options: [ 'Star, solar system, galaxy, universe',
       'Galaxy, solar system, Milky Way, universe',
       'Planet, galaxy, star, solar system'], required: true},
       {prompt: 'Which of the following are located in the nucleus of an atom?',
        options: [ 'Protons and neutrons',
       'Only protons',
       'Only electrons'], required: true},
       {prompt: 'Which of the following has the least mass?',
        options: [ 'An electron',
       'A proton',
       'A neutron'], required: true},
       {prompt: 'What percent of an atom’s space does its nucleus occupy?',
        options: [ 'Less than 1%',
       '10%',
       '50%'], required: true},
       {prompt: 'In the famous equation attributed to Albert Einstein, E=mcˆ2, what does the letter ”m” represent?',
        options: [ 'Mass',
       'Momentum',
       'Moment of inertia'], required: true},
       {prompt: 'If I were to heat up an inflated balloon, which of the the following would occur?',
        options: [ 'The balloon would expand',
       'The balloon would shrink',
       'None of these answers are correct'], required: true},
       {prompt: 'Which of the following is a difference between an electrostatic field and a magnetic field',
        options: [ 'An electrostatic field can have monopoles',
       'A magnetic field can have monopoles',
       'An electrostatic field cannot have dipoles'], required: true},
       {prompt: 'What is one way in which light waves are different from sound waves?',
        options: [ 'Light waves do not require a medium to travel through',
       'Sound waves do not require a medium to travel through',
       'Light waves require a medium to travel through'], required: true},
       {prompt: 'Which of the following is a correct statement about light waves:',
        options: [ 'Higher frequency correlates to higher energy',
       'Shorter wavelength correlates to lower frequency',
       'Lower frequency correlates to higher energy'], required: true},
       {prompt: 'Order the following electromagnetic wavelengths from longest to shortest: radio waves, visible light, x-rays',
        options: [ 'Radio waves, visible light, x-rays',
       'Radio waves, x-rays, visible light',
       'X-rays, radio waves, visible light'], required: true},
       {prompt: 'Which of the following is a scalar quantity?',
        options: [ 'Energy',
       'Velocity',
       'Acceleration'], required: true},
       {prompt: 'Which of the following is a vector quantity?',
        options: [ 'Displacement',
       'Speed',
       'Mass'], required: true},
       {prompt: 'Which of the following is an example of a simple machine?',
        options: [ 'All of the above',
       'Lever',
       'Wheelbarrow'], required: true},
       {prompt: 'Which type of energy is stored in an object due to its position or height?',
        options: [ 'Gravitational potential energy',
       'Kinetic energy',
       'Thermal energy'], required: true},
       {prompt: 'What is the term used to describe an atom that has gained or lost electrons?',
        options: [ 'Ion',
       'Isotope',
       'Nucleus'], required: true},
       {prompt: 'What is the term used to describe the emission of particles or radiation from an unstable nucleus?',
        options: [ 'Decay',
       'Radioactivity',
       'Fission'], required: true},
       {prompt: 'Which of the following is a unit of force?',
        options: [ 'Newton',
       'Joule',
       'Watt'], required: true},
       {prompt: 'How does the mass of an object affect its acceleration when a constant force is applied to it?',
        options: [ 'The mass and acceleration are inversely proportional',
       'The mass and acceleration are directly proportional',
       'The mass has no effect on acceleration'], required: true},
       {prompt: 'What is the process by which a solid turns directly into a gas without passing through the liquid state?',
        options: [ 'Sublimation',
       'Melting',
       'Evaporation'], required: true},
       {prompt: 'Which type of energy is associated with the motion of atoms and molecules?',
        options: [ 'Thermal energy',
       'Kinetic Energy',
       'Potential Energy'], required: true},
       {prompt: 'Which type of circuit has more than one pathway for electric current to flow?',
        options: [ 'Parallel circuit',
       'Series circuit',
       'Closed circuit'], required: true},
       {prompt: 'The north pole of the magnetized needle within a compass points toward which of Earth’s poles:',
        options: [ 'Magnetic north pole',
       'Magnetic south pole',
       'Geographic north pole'], required: true},
       {prompt: 'Which of the following is true of the speed of light?',
        options: [ 'It is the fastest speed in physics',
       'It is slower than the speed of sound',
       'It is unknown'], required: true},
       {prompt: 'Order the following colors from shortest to longest wavelength: blue, red, yellow',
        options: [ 'Blue, yellow, red',
       'Red, yellow, blue',
       'Yellow, blue, red'], required: true},
       {prompt: 'Which of the following is a measure of the amount of matter in an object?',
        options: [ 'Mass',
       'Weight',
       'Density'], required: true},
       {prompt: 'In which direction does a positively charged object move when placed in an electric field?',
        options: [ 'Towards the field',
       'Away from the field',
       'In a circular motion around the field'], required: true},
       {prompt: 'How does the resistance of a wire change as its diameter increases?',
        options: [ 'It decreases',
       'It increases',
       'It remains constant'], required: true}
       ]

var qsets = [qset1, qset2, qset3];

// loop through questions and answers and randomize
var rand_qsets = new Object();
var i; var j;
for (i = 0; i < qsets.length; i++) {
  var temp_qs = qsets[i];
  for (j = 0; j < temp_qs.length; j++) {
    temp_qs[j].options = jsPsych.randomization.shuffle(temp_qs[j].options)
  }
  rand_qsets[i] = jsPsych.randomization.shuffle(temp_qs);
}

var final_qsets = new Object();
final_qsets[0] = jsPsych.randomization.shuffle([rand_qsets[0][0],rand_qsets[0][1],rand_qsets[0][2],rand_qsets[0][3],rand_qsets[0][4],
                                                rand_qsets[1][0],rand_qsets[1][1],rand_qsets[1][2],rand_qsets[1][3],rand_qsets[1][4],
                                                rand_qsets[2][0],rand_qsets[2][1],rand_qsets[2][2]])

final_qsets[1] = jsPsych.randomization.shuffle([rand_qsets[0][5],rand_qsets[0][6],rand_qsets[0][7],rand_qsets[0][8],rand_qsets[0][9],
                                                rand_qsets[1][5],rand_qsets[1][6],rand_qsets[1][7],rand_qsets[1][8],rand_qsets[1][9],
                                                rand_qsets[2][3],rand_qsets[2][4],rand_qsets[2][5]])

final_qsets[2] = jsPsych.randomization.shuffle([rand_qsets[0][10],rand_qsets[0][11],rand_qsets[0][12],rand_qsets[0][13],rand_qsets[0][14],
                                                rand_qsets[1][10],rand_qsets[1][11],rand_qsets[1][12],rand_qsets[1][13],rand_qsets[1][14],
                                                rand_qsets[2][6],rand_qsets[2][7],rand_qsets[2][8]])

//let test = final_qsets[1];
//console.log(final_qsets[1].splice(1,1))

// run experiment
var runExperiment = function(options) {

  //fullscreen mode
  var fscreen = {
    type: 'fullscreen',
    message: '<p>We’d like you to really focus on this HIT so that we can collect clean data. Please turn off any music (but keep your volume turned on), close any additional open tabs in your browser (or any other open programs), remove any distractions around you (e.g. phone), and make yourself comfortable. When you are ready, please press the following button to switch your browser to fullscreen mode. (Your browser will remain in fullscreen for the duration of the HIT.  If you need to exit the HIT early, you may press ESCAPE (esc) to exit fullscreen mode and return your browser back to normal.</p>',
    button_label: 'Enter fullscreen mode',
    fullscreen_mode: true
  };
  experimentTimeline.push(fscreen)

  var soundcheck_movie = {
    type: "instructions",
    pages: ["<h2>Speaker adjustment</h2><p>Click the button to play the following sound clip:</p>" +
            "<audio id='soundTest' src='static/files/furelise.mp3' preload='auto'></audio>" +
            "<button style='background-color:white; outline:none' class='btn btn-large' onclick='document.getElementById(" + '"soundTest"' + ").play();'><i class='fa fa-play-circle-o fa-5x'></i></button>" +
            "<p>Take this time to adjust your speaker or headphone volume to a comfortable level. Press the spacebar to continue to the next screen once you are ready.</p>"],
    key_forward: 32
  }
  experimentTimeline.push(soundcheck_movie);

  // opening instructions
  var open_instructions = {
    type: "instructions",
    pages: ["<div class='instructions'> <p style='font-weight:bold'> PLEASE READ THESE INSTRUCTIONS CAREFULLY</p>" +
            "<p>In this experiment, you will watch informational videos and answer questions about Cosmology and Astronomy.</p>" +
            "<p>In total, you will be asked <strong>three</strong> sets of <strong>thirteen</strong> questions and you will watch <strong>two</strong> videos.</p>" +
            "<p>Press the spacebar to continue.</p></div>",
            "<div class='instructions'> <p>You will start the experiment by answering a set of thirteen questions about Cosmology and Astronomy.</p>" +
            "<p>Even though you will not have watched an informational video yet, try to answer the questions to the best of your ability.</p>" +
            "<p>Press the spacebar to continue.</p></div>",
            "<div class='instructions'> <p>After you anwer the first set of questions, you will watch the informational videos and answer some more questions after each video.</p>" +
            "<p>Please, pay attention to the informational videos and try to learn about Cosmology and Astronomy.</p>" +
            "<p>Then, try to use the knowledge you learned from the videos to answer the following questions.</p>" +
            "<p>Press the spacebar to continue.</p></div>",
            "<div class='instructions'> <p>Okay that's everything! Ready to start?</p>" +
            "<p><strong>When you're ready to begin the first set of questions, press the spacebar.</strong></p></div>"],
    key_forward: 32
  };
  experimentTimeline.push(open_instructions);

  // test questions
  var test = {
    type: 'survey-multi-choice',
    questions: final_qsets[0],
    on_finish: function() {
      console.log('Saving quiz data...')
      psiTurk.recordTrialData(final_qsets[0])
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
            "<p><strong>When you're ready to begin watching the first video, press the spacebar.</strong></p></div>"],
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
    pages: ["<div class='instructions'><p>Now you will answer some questions about Cosmology and Astronomy. Please, answer the questions to the best of your ability.</p>" +
            "<p><strong>When you're ready to begin answering the questions, press the spacebar.</strong></p></div>"],
    key_forward: 32
  };
  experimentTimeline.push(test2_instructions);

  // test questions
  var test2 = {
    type: 'survey-multi-choice',
    questions: final_qsets[1],
    on_finish: function() {
      console.log('Saving quiz data...')
      psiTurk.recordTrialData(final_qsets[1])
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
            "<p><strong>When you're ready to begin watching the second video, press the spacebar.</strong></p></div>"],
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

  // test instructions
  var test3_instructions = {
    type: "instructions",
    pages: ["<div class='instructions'><p>Now you will answer some questions about Cosmology and Astronomy. Please, answer the questions to the best of your ability.</p>" +
            "<p><strong>When you're ready to begin answering the questions, press the spacebar.</strong></p></div>"],
    key_forward: 32
  };
  experimentTimeline.push(test3_instructions);

  // test questions
  var test3 = {
    type: 'survey-multi-choice',
    questions: final_qsets[2],
    on_finish: function() {
      psiTurk.recordTrialData(final_qsets[2])
      console.log('Saving quiz data...')
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
    pages: ["<h2>Your <b>Debriefing</b> goes here</h2>" +
            "<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>" +
            "<p>Amet venenatis urna cursus eget nunc scelerisque. In massa tempor nec feugiat nisl pretium fusce id.</p>" +
            "<p>enenatis urna cursus eget nunc. Curabitur gravida arcu ac tortor dignissim. Volutpat sed cras ornare arcu dui vivamus. Viverra orci sagittis eu volutpat odio facilisis mauris. Convallis convallis tellus id interdum velit laoreet id donec ultrices. Mi eget mauris pharetra et ultrices neque ornare. Et ligula ullamcorper malesuada proin libero nunc consequat interdum varius. Sit amet tellus cras adipiscing enim eu turpis egestas pretium.</p>" +
            "<p>Nunc consequat interdum varius sit. Viverra justo nec ultrices dui sapien eget mi. Ornare aenean euismod elementum nisi. Dignissim suspendisse in est ante in nibh mauris. Imperdiet nulla malesuada pellentesque elit eget gravida cum sociis. Eget magna fermentum iaculis eu non diam phasellus. At erat pellentesque adipiscing commodo. Nullam ac tortor vitae purus. Elementum facilisis leo vel fringilla est ullamcorper eget nulla. Lacus luctus accumsan tortor posuere. Ac orci phasellus egestas tellus. Mi proin sed libero enim sed faucibus turpis in. Cursus in hac habitasse platea dictumst. Purus gravida quis blandit turpis cursus. Pellentesque habitant morbi tristique senectus et netus et malesuada. Praesent elementum facilisis leo vel fringilla est ullamcorper.</p>",
            "<p>Thank you! Please press escape to exit fullscreen mode.</p>"],
    show_clickable_nav: true,
    key_forward: 32
  };
  experimentTimeline.push(finished_message);

  /*start experiment*/
  jsPsych.init({
    timeline: experimentTimeline,
    show_progress_bar: false,
    on_data_update: function(data) {
      psiTurk.recordTrialData(data)
    },
    on_finish: function() {
      console.log('Saving data...')
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
            console.log('Data saved!');
            clearInterval(reprompt);
            psiTurk.completeHIT();
          },
          error: prompt_resubmit  //if error saving data, try again
        });
      };

      psiTurk.saveData({
        success: function() {
          console.log('Data saved!');
          psiTurk.completeHIT();
        },
        error: prompt_resubmit
      });
    },
  });
};
