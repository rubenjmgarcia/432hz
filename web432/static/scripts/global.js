/* global */

/* loading */
$(window).on("load", function(){
    $('.loading-logo').removeClass('animated');
    $('.loading').addClass('loaded').fadeOut(500);
});

setTimeout(function(){
    $('.loading-logo').removeClass('animated');
    $('.loading').addClass('loaded').fadeOut(500);
}, 2500);