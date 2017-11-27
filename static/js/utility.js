function clearCookies() {
    Cookies.remove('userName');
    Cookies.remove('userID');
    Cookies.remove('token');
}

function isLoggedIn() {
    var username = Cookies.get('userName');
    var token = Cookies.get('token');
    var userID = Cookies.get('userID');
    if (username && token && userID) {
        console.log("log");
        return username;
    } else {
        console.log("not log");
        clearCookies();
    }
}