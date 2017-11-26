
$(document).ready(function(){
    var username = isLoggedIn();
    if (username === undefined) {
        $("#loginForm").show();
        $("#profileOptions").hide();
    } else {
        $("#loginForm").hide();
        $("#profileOptions").show();
    }

    $("#loginForm").submit(function(event) {
        event.preventDefault();
        // Cookies.set("username", "testUser");
        // Cookies.set("token", "123455");
        // $("#currentUsername").text(Cookies.get("username"));
        // $("#loginForm").hide();
        // $("#profileOptions").show();
        $.post("http://localhost:5000/login",
            {username : $("#usernameInput").val(),
                passwd : $("#passwordInput").val()
            })
            .done(function(result){
                console.log(result['code']);
                console.log(Cookies.get('userName'));
                console.log(Cookies.get('userID'));
                console.log(Cookies.get('token'));
                alert(Cookies.get('token'));
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
        // $.post("http://",
        //     {username : $("#usernameInput").val().trim(),
        //         password: $("passwordInput").val().trim()
        //     })
        //     .done(function(result){
        //         alert("success" + result["result"]);
        //         result['token'];
        //         result['username'];
        //     })
        //     .fail(function(xhr, textStatus, errorThrown){
        //         console.log(xhr.statusText);
        //         console.log(textStatus);
        //         console.log(errorThrown);
        //     });
    });

});