$(document).ready(function(){
  $("#accordion").on("shown.bs.collapse", function () {
    var element = $(this).find('.collapse.show').prev('.card-header');

    $('html, body').animate({
      scrollTop: $(element).offset().top - $('nav.navbar').outerHeight()
    }, 500);
  });
});
