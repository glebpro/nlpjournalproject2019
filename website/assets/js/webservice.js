var body = '{"input_text":"what did I note about watermelon", "key":"B670F7AB38"}';

//stores what variable is currently hidden
var expanded = "id";

$(document).on("click", "#add", hideOther);
$(document).on("click", "#view", hideOther);
$(document).on("click", ".backarrow", showAction);
$(document).on("click", "#submitEntry", submitEntry);
$(document).on("click", "#searchJournal", searchJournal);


//This is for submitting to the program
function submitEntry(){
    //confirm it passes
    var valid = false;
    if(valid){
        $("#message").text("Entry sucessfully Submitted");
        $("#message").attr( "class", "update");
    }
    else{
        $("#message").text("Error: Issue submitting new note.");
        $("#message").attr( "class", "warning");
    }
}

function searchJournal(){

    var valid = false;

    if(valid){
        //Steps to display data
    }
    else{
        $("#message").text("Error: Searching is not currently working...")
        $("#message").attr("class", "warning");
    }
}


//These are animation based functions
function hideOther(){
    //alert($(this).attr("id"));
    if($(this).attr("id") === "add"){
        expanded = "#add";
        hideLeft(expanded);
        hideRight("#view");
        //expandUp("#add-expand")
    }
    else if($(this).attr("id") === "view"){
        expanded = "#view";
        hideRight(expanded);
        hideLeft("#add");
    }

}
function showAction(){
    var expandId = expanded + "-expand";
    //alert(expandId);
    $(expandId).toggleClass("hide");
    $("#view").toggleClass("hide");
    $("#add").toggleClass("hide");
    $("#add").animate({ left: "0%" }, { duration: 900});
    $("#view").animate({ right: "0%" }, { duration: 900});
    $("#message").toggleClass("hide");
}

function hideLeft(id){
    $(id).animate({ left: "100%" }, { duration: 750, complete: function() {
        $(id).toggleClass('hide');

        if(id === expanded){
            //alert("Here LEft");
            $(expanded + "-expand").toggleClass('hide');
        }
     }});    
}
function hideRight(id){
    $(id).animate({ right: "100%" }, { duration: 750,  complete: function() {
        $(id).toggleClass('hide');

        if(id === expanded){
            //alert("Here right")
            $(expanded +"-expand").toggleClass('hide');
        }
     }});    
}

//validation code
function validate(event) {
    if(expanded === "#add"){
        let entry = $("#newEntry").val();
        if(!entry || entry === "" || entry === " "){
            alert("Please fill out the note before submitting...");
            return false;
        }
        else{
            return true;
        }
    }
    else if(expanded === "#view"){
        let search = $("#search").val();
        if(!search || search == "" || search == " "){
            alert("Please fill out your search field before submitting...");
            return false;
        }
        else{
            return true;
        }
    }

    return false;
  }