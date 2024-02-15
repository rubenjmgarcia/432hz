/* go-to-news */
document.getElementById('go-to-news').addEventListener('click', function() {
    document.getElementById('news-section').scrollIntoView({behavior: "smooth"});
});

/* go-to-section1 */
document.getElementById('go-to-section1').addEventListener('click', function() {
    event.preventDefault();
    document.getElementById('section1').scrollIntoView({behavior: "smooth"});
});