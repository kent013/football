$(document).ready(function(){
  $("#accordion").on("shown.bs.collapse", function () {
    var element = $(this).find('.collapse.show').prev('.card-header');

    $('html, body').animate({
      scrollTop: $(element).offset().top - $('nav.navbar').outerHeight()
    }, 500);
  });
  $("#accordion .card-header h1 a").on("click", function (e) {
    var element = $($(this).parents('.card-header').data('target'));
    if(element.is(":visible")){
      e.stopPropagation();
    }
  });

  $('#search_button').on('click', function (e) {
        e.preventDefault();
        val = $('#search_query').val()
        if(val){
          window.location.href= $('#search_form').attr('action') + $('#search_query').val();
        }
        return false;
    });


  (function () {
    var ans; //1つ前のページが同一ドメインかどうか
    var bs = false; //unloadイベントが発生したかどうか
    var ref = document.referrer;
    $(window).bind("unload beforeunload", function () {
      bs = true;
    });
    re = new RegExp(location.hostname, "i");
    if (ref.match(re)) {
      ans = true;
    } else {
      ans = false;
    }
    $('.historyback').bind("click", function () {
      var that = this;
      if (ans) {
        history.back();
        setTimeout(function () {
          if (!bs) {
            location.href = $(that).attr("href");
          }
        }, 100);
      } else {
        location.href = $(this).attr("href");
      }
      return false;
    });
  })();
});
