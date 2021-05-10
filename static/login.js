function getlogin(user,passwd){

var xmlhttp = new XMLHttpRequest();
console.log(xmlhttp);

xmlhttp.onreadystatechange = function() {
if (this.readyState == 4 && this.status == 200) {(
    if(this.responseText == "error"){
        document.getElementById("message").innerHTML = "There is no User matching given Credentials.";
        document.getElementById("message").style.color = "red";
    }
    if(this.responseText == "user"){
        window.location = "/applicant";
    }
    if(this.responseText == "company"){
        window.location = "/company";
    }

}
};
xmlhttp.open("GET", "calculator?num1="+num1+"&num2="+num2+"&op="+op, true);
xmlhttp.send();
}