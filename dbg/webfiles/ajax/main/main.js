function set_view_to_main(){
    callback=function(http) {
        if (http.readyState==4) {
            status_update("callback for '" + id + "' called");
            document.getElementById(id).innerHTML=http.responseText;
            }
        }
    do_ajax_POST("get buttons","/ajax/main/buttons.py",make_callback("optionbar"));
}


function test_POST() {
    //example of POSTing data to the server using JSON
    var testjdata=({
        "firstName": "John",
        "lastName" : "Smith",
        "age"      : 25,
        "address"  : {
            "streetAddress": "21 2nd Street",
            "city"         : "New York",
            "state"        : "NY",
            "postalCode"   : "10021"
        },
        "phoneNumber": [ {
            "type"  : "home",
            "number": "212 555-1234"
         },
         {
            "type"  : "fax",
            "number": "646 555-4567"
         }
        ]
    });
    do_ajax_POST(testjdata,"/ajax/test_post.py",make_callback("maincontent"));
}

function test_GET() {
    //example of GETing data from the server, remember that we can use "?" for arguments
    do_ajax_GET("/ajax/test_get.py",make_callback("maincontent"));
}