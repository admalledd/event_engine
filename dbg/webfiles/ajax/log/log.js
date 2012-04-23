function set_view_to_log(){
    do_ajax_POST("get buttons","/ajax/log/main.py",make_callback("optionbar"));
    
}


function loggingtool(size){
    this.maxsize=size;//max buffer size
    this.data=[];//raw buffer data

    this.openlog=function(){
        do_ajax_POST("open log","/ajax/log/logger_settings_post.py",make_callback("maincontent"));
    
    }
    this.closelog=function(){
        do_ajax_POST("close log","/ajax/log/logger_settings_post.py",make_callback("maincontent"));
    }
}

var logdata= new loggingtool(25);//the current last lines of the main server log file //(we dont need the webserv log do we? adm)

