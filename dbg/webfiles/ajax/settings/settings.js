function set_view_to_settings(){
    do_ajax_POST("get buttons","/ajax/settings/main.py",make_callback("optionbar"));
    
}

function settings_reset_form(){
    do_ajax_POST("get form","/ajax/settings/main.py",make_callback("maincontent"));

}
function settings_update_form(){
    //duplicate of reset until I think of something better
    do_ajax_POST("get form","/ajax/settings/main.py",make_callback("maincontent"));

}
function settings_post(form,type){

    var jdata = new Object();
    if (type == 'net'){
        jdata.type = "post net form";
        jdata.host = form.elements["host_ip"].value;
        jdata.port = form.elements["host_port"].value;
        jdata.logname = form.elements["logname"].value;
    }
    else if (type == 'setstat'){
    
    }
    do_ajax_POST(jdata,"/ajax/settings/main.py",make_callback("statusbar"));
}
function settings_stat_post(type){
    //send a single simple stat, use for buttons
    do_ajax_POST(type,"/ajax/settings/main.py",make_callback("statusbar"));
}