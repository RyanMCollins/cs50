var form = document.getElementsByTagName('form')[0];
var username = document.getElementsByName('username')[0];

// Listen for submit
form.addEventListener("submit", function(e) {

    // Prevent submission
    e.preventDefault();

    // Check that username is valid
    $.get("/check?username=" + username.value, function(response) {
        (function(r) {
            if (r) {
                form.submit();
            } else {
                alert("Choose another username");
            }
        })(response);
    });
}, false);