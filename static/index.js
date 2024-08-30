let isShowing = false;

function showhide() {
    let pwd = document.getElementById("pwd");
    let sh = document.getElementById("sh");
    if(isShowing) {
        sh.innerHTML = "hide";
        pwd.type = "text";
    }else {
        sh.innerHTML = "show";
        pwd.type = "password";
    }
    isShowing = !isShowing;
    
}