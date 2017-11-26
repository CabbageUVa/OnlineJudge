function clearCookies() {
    Cookies.remove('username');
    Cookies.remove('token');
}

function isLoggedIn() {
    var username = Cookies.get('username');
    var token = Cookies.get('token');
    if (username && token) {
        console.log("log");
        return username;
    } else {
        console.log("not log");
        clearCookies();
    }
}