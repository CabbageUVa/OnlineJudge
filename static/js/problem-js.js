
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
        $.post("http://localhost/login",
            {username : $("#usernameInput").val(),
                passwd : $("#passwordInput").val()
            })
            .done(function(result){
                var code = result['code'];
                if (code === '200') {
                    $("#loginForm").hide();
                    $("#currentUsername").text(Cookies.get('userName'));
                    $("#profileOptions").show();
                    $("#loginAlert").hide();
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
        $.post("http://localhost/signUp",
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
                    $("#usernameSignup").val('');
                    $("#emailSignup").val('');
                    $("#passwordSignup").val('');
                    $('#signUpCheckbox').prop('checked', false);
                    $("#passwordSignupRepeat").val('');
                    $('#signUpModal').modal('hide');
                    $("#loginAlert").hide();
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

    $("#submitCode").click(function(e){
        e.preventDefault();
        $.post("http://localhost/uploader",
            { code : cppEditor.getValue(),
                Q_ID : problemNumber})
            .done(function(result){
                var code = result['code'];
                if (code === '200') {
                    alert("pass");
                } else if (code === '201') {
                    clearCookies();
                    alert("relogin");
                } else {
                    alert("server error.");
                }
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
    var cppEditor = CodeMirror.fromTextArea(document.getElementById("cpp-code"), {
        lineNumbers: true,
        matchBrackets: true,
        mode: "text/x-c++src"
    });
    $.post("http://localhost/problemDetail",
        {QID : problemNumber} )
        .done(function(result){
            var code = result['code'];
            if (code === '200') {
                var title = result['title'];
                var description = result['description'];
                var difficulty = result['difficulty'];
                var pSubmitNum = result['pSubmitNum'];
                var pAcceptNum = result['pAcceptNum'];
                var defaultCode = result['defaultCode'];
                console.log(title);
                console.log(description);
                console.log(defaultCode);
                $("#title").text(title);
                $("#description").append(description);
                cppEditor.setValue(defaultCode);
            } else {
                alert("server error.");
            }
        })
        .fail(function(xhr, textStatus, errorThrown){
            console.log(xhr.statusText);
            console.log(textStatus);
            console.log(errorThrown);
        });
});