/*
    ThePolka.Cloud™ Store JavaScript
    Client-side enhancements
*/


document.addEventListener("DOMContentLoaded", function () {

    console.log("ThePolka.Cloud™ Store loaded");


    // Highlight current navigation item
    const links = document.querySelectorAll(".nav-link");

    links.forEach(link => {

        link.addEventListener("click", function () {

            links.forEach(item => {
                item.classList.remove("active");
            });

            this.classList.add("active");

        });

    });


});
