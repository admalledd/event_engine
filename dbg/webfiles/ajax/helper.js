
function make_ajax_POST(data,url,callback) {
    var http;
    if (window.XMLHttpRequest) {
        // code for IE7+, Firefox, Chrome, Opera, Safari
        http=new XMLHttpRequest();
        }
    else {// code for IE6, IE5
        http=new ActiveXObject("Microsoft.XMLHTTP");
        }
    http.onreadystatechange=function (){ callback(http) };
    http.open("POST",url,true);
    http.setRequestHeader("Content-type", "application/json");
    http.setRequestHeader("Content-length", data.length);
    http.setRequestHeader("Connection", "close");
    http.send(JSON.stringify(data));
}

function make_ajax_GET(url,callback) {
    var http;
    if (window.XMLHttpRequest) {
        // code for IE7+, Firefox, Chrome, Opera, Safari
        http=new XMLHttpRequest();
        }
    else {// code for IE6, IE5
        http=new ActiveXObject("Microsoft.XMLHTTP");
        }
    http.onreadystatechange=function (){ callback(http) };
    http.open("GET",url,true);
    //http.setRequestHeader("Content-type", "application/json");
    //http.setRequestHeader("Content-length", data.length);
    //http.setRequestHeader("Connection", "close");
    http.send();
}
function make_callback(id) {
    return function(http) {
        if (http.readyState==4) {
            document.getElementById(id).innerHTML=http.responseText;
            }
        }
}