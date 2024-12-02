
window.addEventListener('DOMContentLoaded', event => {

    // Navbar shrink function
    var navbarShrink = function () {
        const navbarCollapsible = document.body.querySelector('#mainNav');
        if (!navbarCollapsible) {
            return;
        }
        if (window.scrollY === 0) {
            navbarCollapsible.classList.remove('navbar-shrink')
        } else {
            navbarCollapsible.classList.add('navbar-shrink')
        }

    };

    // Shrink the navbar 
    navbarShrink();

    // Shrink the navbar when page is scrolled
    document.addEventListener('scroll', navbarShrink);

    //  Activate Bootstrap scrollspy on the main nav element
    const mainNav = document.body.querySelector('#mainNav');
    if (mainNav) {
        new bootstrap.ScrollSpy(document.body, {
            target: '#mainNav',
            rootMargin: '0px 0px -40%',
        });
    };

    // Collapse responsive navbar when toggler is visible
    const navbarToggler = document.body.querySelector('.navbar-toggler');
    const responsiveNavItems = [].slice.call(
        document.querySelectorAll('#navbarResponsive .nav-link')
    );
    responsiveNavItems.map(function (responsiveNavItem) {
        responsiveNavItem.addEventListener('click', () => {
            if (window.getComputedStyle(navbarToggler).display !== 'none') {
                navbarToggler.click();
            }
        });
    });

});

// this function redirects the user to logged in page once details are filled
document.getElementById('login').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission
    window.location.href = 'loggedin.html';
});

// This function tracks the click count
let clickCount = 0;
function countClicks() {
    clickCount++;
    document.getElementById("clicks").innerHTML = `Likes: ${clickCount}`;
}
function newFunction() {
    document.getElementById("clicks").addEventListener("click", countClicks); 
}
newFunction();

// This function allows the user to change their profile picture
function changeImage(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('profileImage').src = e.target.result;
        };
        reader.readAsDataURL(file);
    }
}

// function searchTool() {
//     // Get the search input value and convert it to lowercase for case-insensitive comparison
//     var input = document.getElementById('searchbar');
//     var filter = input.value.toLowerCase();
//     var ul = document.getElementById("list");
//     var li = ul.getElementsByTagName('li');

//     // Show the list if the input is not empty
//     if (filter.length > 0) {
//         ul.style.display = "block"; // Show the list

//         // Loop through all list items and hide those that don't match the search query
//         for (var i = 0; i < li.length; i++) {
//             var a = li[i].getElementsByTagName("a")[0];
//             if (a.innerText.toLowerCase().indexOf(filter) > -1) {
//                 li[i].style.display = ""; // Show the item if it matches
//             } else {
//                 li[i].style.display = "none"; // Hide the item if it doesn't match
//             }
//         }
//     } else {
//         ul.style.display = "none"; // Hide the list if the input is empty
//     }
// }

document.getElementById('searchButton').addEventListener('click', searchTool);

function searchTool() {
    // Get the search input value and convert it to lowercase for case-insensitive comparison
    var input = document.getElementById('searchbar');
    var filter = input.value.toLowerCase();
    var ul = document.getElementById("list");
    var li = ul.getElementsByTagName('li');

    // Show the list if the input is not empty
    if (filter.length > 0) {
        ul.style.display = "block"; // Show the list

        // Loop through all list items and hide those that don't match the search query
        for (var i = 0; i < li.length; i++) {
            var a = li[i].getElementsByTagName("a")[0];
            if (a.innerText.toLowerCase().indexOf(filter) > -1) {
                li[i].style.display = ""; // Show the item if it matches
            } else {
                li[i].style.display = "none"; // Hide the item if it doesn't match
            }
        }
    } else {
        ul.style.display = "none"; // Hide the list if the input is empty
    }
}

function previewImage(event) {
    var reader = new FileReader();
    reader.onload = function(){
        var output = document.getElementById('profilePreview');
        output.src = reader.result;
        output.style.display = 'block';
    };
    reader.readAsDataURL(event.target.files[0]);
}