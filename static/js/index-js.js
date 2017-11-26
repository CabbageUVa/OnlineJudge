
function showSignUpModal() {
    if(isLoggedIn()) {
        alert("Please log out first");
    } else {
        $('#signUpModal').modal('show');
    }
}

$(document).ready(function(){
    var username = isLoggedIn();
    if (username === undefined) {
        $("#loginForm").show();
        $("#profileOptions").hide();
    } else {
        $("#loginForm").hide();
        $("#currentUsername").text(Cookies.get('userName'));
        $("#profileOptions").show();
    }

    $("#loginForm").submit(function(event) {
        event.preventDefault();
        $.post("http://localhost:5000/login",
            {username : $("#usernameInput").val(),
                passwd : $("#passwordInput").val()
            })
            .done(function(result){
                var code = result['code'];
                if (code === '200') {
                    $("#loginForm").hide();
                    $("#currentUsername").text(Cookies.get('userName'));
                    $("#profileOptions").show();
                } else if (code === '201') {
                    alert("wrong password.");
                    $("#usernameInput").val('');
                    $("#passwordInput").val('');
                } else {
                    alert("server error.");
                    $("#usernameInput").val('');
                    $("#passwordInput").val('');
                }
                
                console.log(result['code']);
                console.log(Cookies.get('userName'));
                console.log(Cookies.get('userID'));
                console.log(Cookies.get('token'));
            })
            .fail(function(xhr, textStatus, errorThrown){
                console.log(xhr.statusText);
                console.log(textStatus);
                console.log(errorThrown);
            });

    });
    $("#registerForm").submit(function(event) {
        event.preventDefault();
        $.post("http://localhost:5000/signUp",
            {username : $("#usernameSignup").val(),
                email : $("#emailSignup").val(),
                passwd : $("#passwordSignup").val()
            })
            .done(function(result){
                var code = result['code'];
                if (code === '200') {
                    $("#loginForm").hide();
                    $("#currentUsername").text(Cookies.get('userName'));
                    $("#profileOptions").show();
                } else if (code === '201') {
                    alert("username has been taken.");
                    $("#usernameSignup").val('');
                } else if (code == '202') {
                    alert("email has been taken.");
                    $("#emailSignup").val('');
                } else {
                    alert("server error.");
                    $("#usernameInput").val('');
                    $("#passwordInput").val('');
                }
                console.log(result['code']);
                console.log(Cookies.get('userName'));
                console.log(Cookies.get('userID'));
                console.log(Cookies.get('token'));
            })
            .fail(function(xhr, textStatus, errorThrown){
                console.log(xhr.statusText);
                console.log(textStatus);
                console.log(errorThrown);
            });

    });

    $("#logoutButton").click(function(event) {
        event.preventDefault();
        clearCookies();
        $("#currentUsername").text("Nobody");
        $("#loginForm").show();
        $("#profileOptions").hide();
    });
});