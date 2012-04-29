function auto_update() {
    callback=function(http) {
        if (http.readyState==4) {
            //update what text needs updating based on what the server pushed to us (json data)
            document.getElementById("statusbar").innerHTML=http.responseText;
            jdata = JSON.parse(http.responseText);
            if (jdata.hasOwnProperty("log_update")){
                //we have a log update. note that we get only the newest lines since our last call, here is where we limmit the number displayed
                //log_update is in the form of "log_update":{"text":["new","linex"],"total_length":500} where total_length is the full log file size in lines
                logdata.data = jdata.log_update.text;
                
                //test only code!
                document.getElementById("maincontent").innerHTML=logdata.data.join('<br />');
            }
            
            if (jdata.hasOwnProperty("layout_update")){
                document.getElementById("maincontent").innerHTML=jdata.layout_update.maincontent;
                document.getElementById("optionbar").innerHTML=jdata.layout_update.optionbar;
                document.getElementById("statusbar").innerHTML=jdata.layout_update.reason;
                window.location.hash=jdata.layout_update.newpath;
                
            }
            if (jdata.hasOwnProperty("netobjs")){
                document.getElementById("netobj_form").innerHTML=jdata.netobjs.netlist;
                document.getElementById("netobj_data").innerHTML=jdata.netobjs.status;
            }
            
            
            else {
                //the data sent does not match any plans that we have already placed, set the statusbar to this odd data
                document.getElementById("statusbar").innerHTML=http.responseText;
            }
        }
    }
    //add the current selected window to the GET as a query string
    var path = "/ajax/auto_update.py?"+window.location.hash.split('#')[1];
    do_ajax_GET(path,callback);
    setTimeout("auto_update()",2500);
}
setTimeout("auto_update()",5000); //example code for auto update function