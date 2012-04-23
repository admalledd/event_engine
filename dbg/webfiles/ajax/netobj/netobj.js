function set_view_to_netobj(){
    do_ajax_POST("get buttons","/ajax/netobj/main.py",make_callback("optionbar"));
    
}

function netobj_reset_form(){
    do_ajax_POST("get form","/ajax/netobj/main.py",make_callback("maincontent"));

}
function netobj_update_form(){
    //duplicate of reset until I think of something better
    do_ajax_POST("get form","/ajax/netobj/main.py",make_callback("maincontent"));

}
function netobj_post(form,type){

    var jdata = new Object();
    if (type == 'newobj'){
        jdata.type = "newobj";
        jdata.oid = form.elements["OID"].value;
        jdata.objtype = form.elements["objtype"].value;
    }
    else if (type == 'setstat'){
    
    }
    do_ajax_POST(jdata,"/ajax/netobj/main.py",make_callback("statusbar"));
}
function netobj_stat_post(type){
    //send a single simple stat, use for buttons
    do_ajax_POST(type,"/ajax/netobj/main.py",make_callback("statusbar"));
}