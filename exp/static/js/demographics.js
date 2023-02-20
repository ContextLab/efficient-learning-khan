var runDemographics = function(options) {
  window.onload = function() {
    $("body").append("<div id='googleform'><iframe src='https://docs.google.com/forms/d/e/1FAIpQLSfsAsQ1NlKa26G3Q2EwI6gq_kW599LhMkwCa7Q9XCJLB7Ow2A/viewform?embedded=true' width='" +
        $(window).width() + "' height='" +
        $(window).height() + "' frameborder='0' marginheight='0' marginwidth='0'>Loading...</iframe></div>")

    $("body").append("<button class='btn btn-success' id='nextBtn' style='position: fixed; bottom: 0px; right: 0px;' id='fixedbutton'>Done</button>")

    $('#nextBtn').click(function() {
      $("body").remove();
      runExperiment(options);
    });
  };
};
