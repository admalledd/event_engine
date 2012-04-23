
function do_ajax_POST(data,url,callback) {
    /*
    data is a javascript data object, NOT a string to be sent!
    
    */
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
    status_update("ajax POST to '"+url+"' sent");
}

function do_ajax_GET(url,callback) {
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
    http.send();
    status_update("ajax GET to '"+url+"' sent");
}
function make_callback(id) {
    /*
    makes a callback for either POSTing or GETing via ajax.
    
    note that we will probably want to change the default action to actually replace the data given inside a JSON object in the future.
    
    */
    return function(http) {
        if (http.readyState==4) {
            status_update("callback for '" + id + "' called");
            document.getElementById(id).innerHTML=http.responseText;
            }
        }
}
function status_update(text) {
    document.getElementById("statusbar").innerHTML=text;
}
