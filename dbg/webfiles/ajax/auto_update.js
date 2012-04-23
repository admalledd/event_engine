function auto_update() {
    callback=function(http) {
        if (http.readyState==4) {
            //update what text needs updating based on what the server pushed to us (json data)
            
            jdata = JSON.parse(http.responseText);
            if (jdata.hasOwnProperty("log_update")){
                //we have a log update. note that we get only the newest lines since our last call, here is where we limmit the number displayed
                //log_update is in the form of "log_update":{"text":["new","linex"],"total_length":500} where total_length is the full log file size in lines
                logdata.data = jdata.log_update.text;
                
                //test only code!
                document.getElementById("maincontent").innerHTML=logdata.data.join('<br />');
            }
            
            else if (jdata.hasOwnProperty("layout_update")){
            
            }
            
            else {
                //the data sent does not match any plans that we have already placed, set the statusbar to this odd data
                document.getElementById("statusbar").innerHTML=http.responseText;
            }
        }
    }
    do_ajax_GET("/ajax/auto_update.py",callback);
    setTimeout("auto_update()",2500);
}
setTimeout("auto_update()",500); //example code for auto update function