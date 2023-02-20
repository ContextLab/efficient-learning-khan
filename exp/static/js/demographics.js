var runDemographics = function(options) {
  window.onload = function() {
    $("body").append("<div id='googleform'><iframe src='https://docs.google.com/forms/d/e/1FAIpQLSfBL9Q7UNQg9q8lbO-TkKJpdaCS4thMr3x-MjpC_q0xOfA77w/viewform?embedded=true' width='" +
        $(window).width() + "' height='" +
        $(window).height() + "' frameborder='0' marginheight='0' marginwidth='0'>Loading...</iframe></div>")

    $("body").append("<button class='btn btn-success' id='nextBtn' style='position: fixed; bottom: 0px; right: 0px;' id='fixedbutton'>Done</button>")

    $('#nextBtn').click(function() {
      $("body").remove();
      runExperiment(options);
    });
  };
};
