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

/* carousel */
$('.carousel .carousel-item').not(".normal-carousel").each(function(){
    var next = $(this).next();
    if (!next.length){
        next = $(this).siblings(':first');
    }
    next.children(':first-child').clone().appendTo($(this));
    for (var i=0;i<3;i++){
        next=next.next();
        if (!next.length){
            next = $(this).siblings(':first');
        }
        next.children(':first-child').clone().appendTo($(this));
    }
});

/* copy_url 
function copy_url() {
    var url = '{% if session['lang'] == 'pt' %}{{ news_post.news_url_pt }}{% else %}{{ news_post.news_url_en }}{% endif %}';

    var tempInput = document.createElement("input");
    tempInput.value = url;
    document.body.appendChild(tempInput);
    tempInput.select();
    document.execCommand("copy");
    document.body.removeChild(tempInput);
    
    // Optional: Show a tooltip or a message indicating that the link has been copied
    var tooltip = document.getElementById("copy-url");
    tooltip.setAttribute("data-original-title", "Link copiado!");
    $(tooltip).tooltip('show'); // Assuming you are using jQuery for Bootstrap tooltips
}*/
