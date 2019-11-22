var form = document.getElementsByTagName('form')[0];
var fullname = document.getElementById('name');
var email = document.getElementById('email');
var school = document.getElementById('school');
var loc = document.getElementById('location');
var standing = document.getElementById('standing');
var interest = document.getElementsByName('interest')

// Listen for submit
form.addEventListener("submit", function(e) {
    // See if at least one interest is checked
    var interestBool = false;
    interest.forEach(function(e) {
        interestBool = interestBool || e.checked;
    });

    // Prevent submission
    e.preventDefault();

    // Send alert if any values are missing, otherwise submit
    if (!fullname.value) {
        alert("Please enter your name");
    } else if (!email.value) {
        alert("Please enter your email");
    } else if (!school.value) {
        alert("Please enter the name of your school");
    } else if (!loc.value) {
        alert("Please enter your location");
    } else if (standing[0].selected) {
        alert("Please enter your current standing");
    } else if (interestBool == false) {
        alert("Please check at least one area of interest");
    } else {
        this.submit();
    }
}, false);

