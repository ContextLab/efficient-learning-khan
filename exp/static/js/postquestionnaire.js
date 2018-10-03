var runPostQuestionnaire = function(options) {
  $("body").append("<div id='googleform'><iframe src='https://docs.google.com/forms/d/e/1FAIpQLSdj6IV19P50l3Ee4fjTUWDyTEuOcwaVIVDOMlCRoQ6aKbtfjw/viewform?embedded=true' width='" +
      $(window).width() + "' height='" +
      $(window).height() + "' frameborder='0' marginheight='0' marginwidth='0'>Loading...</iframe></div>")

  $("body").append("<button class='btn btn-success' id='finishedBtn' style='position: fixed; bottom: 0px; right: 0px;' id='fixedbutton'>Finished!</button>")

  $('#finishedBtn').click(function() {
      psiTurk.completeHIT();
  });
};
