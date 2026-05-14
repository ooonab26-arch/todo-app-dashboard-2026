

function doneScheduled(id, priority) {

    fetch('/done/' + id)
    .then(() => {
        var row = document.getElementById(id);

        // remove parent styling
        var cellParent = document.getElementById(id).parentElement;

        // get background color of parent
        var cellParentColor = cellParent.style.backgroundColor;

        // if background color is #f6f6f6, note is done
        if (cellParentColor == "rgb(246, 246, 246)") {

            if (priority == "0") {
                cellParent.style = "max-width: calc( 15 * 1vw ); background-color: #e1ffee; text-decoration:; color: #939393;";
            } else if (priority == "1") {
                cellParent.style = "max-width: calc( 15 * 1vw ); background-color: #fbf6cd; text-decoration:; color: #939393;";
            } else if (priority == "2") {
                cellParent.style = "max-width: calc( 15 * 1vw ); background-color: #ffe1e1; text-decoration:; color: #939393;";
            }      
        }
        else{
            cellParent.style = "max-width: calc( 15 * 1vw ); background-color: #f6f6f6; text-decoration: line-through;  color: #939393;";
            
            // call cancel edit function
            cancelEdit();

            // confetti
            loadFunction(true);
        }
    })
}


function doneAllDay(id, priority) {

    fetch('/done/' + id)
    .then(() => {

        var row = document.getElementById(id);

        // if note is done then make it undone
        if (row.style.backgroundColor == "rgb(246, 246, 246)") {
            console.log(row.childNodes[1].childNodes[1].childNodes[3].childNodes[1]);
            row.style.textDecoration = "none";
            row.style.backgroundColor = "#ffffff";
            row.style.color = "#172b4d";

            // change badge color based on priority
            if (priority == "0") {
                row.querySelectorAll('span')[0].classList = "badge bg-gradient-success";
            }
            else if (priority == "1") {
                row.querySelectorAll('span')[0].classList = "badge bg-gradient-warning";
            }
            else if (priority == "2") {
                row.querySelectorAll('span')[0].classList = "badge bg-gradient-danger";
            }


            data = row.childNodes[1].childNodes[1].childNodes[3].childNodes[1]
            data.style.textDecoration = "none";
            data.style = "max-width: calc( 30 * 1vw ); color: #172b4d; ";
            // data.classList = "align-left text-center text-secondary  text-sm";
        }
        // if note is undone then make it done
        else {
            row.style.backgroundColor = "#f6f6f6";
            row.style.textDecoration = "line-through";
            
            // make text color #939393;
            row.style.color = "#939393";

            // change badge to badge bg-gradient-light
            row.querySelectorAll('span')[0].classList = "badge bg-gradient-light";

            // move the task to the top of the table
            // var table = document.getElementById("all-day-table");
            // table.insertBefore(row, table.childNodes[0]);
            
            // confetti
            loadFunction(true);
        }
    })
    // call cancel edit function
    cancelEdit();

    
}

function moveToTomorrow(id) {

    fetch('/updatetime/' + id + '/+')
    .then(() => {
        var row = document.getElementById(id);

        // remove parent styling
        var cellParent = document.getElementById(id).parentElement;
        cellParent.style.backgroundColor = "";
        cellParent.style = "border-right: 1px solid #e7e7e7; border-left: 1px solid #e7e7e7;";
        cellParent.ondrop = function(event) { drop(event); };
        cellParent.ondragover = function(event) {  allowDrop(event); };

        // remove the task from the table
        row.parentNode.removeChild(row);
    })
    cancelEdit();
}

function removeTask(id) {

    fetch('/remove/' + id)
    .then(() => {
        var row = document.getElementById(id);

        // remove parent styling
        var cellParent = document.getElementById(id).parentElement;
        cellParent.style.backgroundColor = "";
        cellParent.style = "border-right: 1px solid #e7e7e7; border-left: 1px solid #e7e7e7;";
        cellParent.ondrop = function(event) { drop(event); };
        cellParent.ondragover = function(event) {  allowDrop(event); };

        // remove the task from the table
        row.parentNode.removeChild(row);
    })
    cancelEdit();
}

function allowDrop(ev) {
    ev.preventDefault();
}

var globalItemColor;
var globalItemType;

function drag(ev) {
    ev.dataTransfer.setData("text", ev.target.id);

    // get item type like DIV or TR
    var cell= document.getElementById(ev.target.id);
    globalItemType = cell.tagName;

    // get parent of element of id
    var cellParent = document.getElementById(ev.target.id).parentElement;
    globalItemColor = cellParent.style.backgroundColor;

    // clear cell background color
    cellParent.style.backgroundColor = "";
    cellParent.style = "border-right: 1px solid #e7e7e7; border-left: 1px solid #e7e7e7;";
    cellParent.ondrop = function(event) {
        drop(event);
    };
    
    cellParent.ondragover = function(event) {
        allowDrop(event);
    };
}

function drop(ev) {
    ev.preventDefault();
    var id = ev.dataTransfer.getData("text");

    var targetTime = ev.target.id;

    // for all-day table
    if (globalItemType == "TR")
    {
        fetch('/updatetime/' + id + '/' + targetTime)
        .then(() => {
        window.location.href = window.location.href;
        })
    }
    // for schedule table
    else if (globalItemType == "DIV")
    {
        ev.target.appendChild(document.getElementById(id));

        // get parent of element of id
        var cellParent = document.getElementById(id).parentElement;
        
        // set cell background color to red
        cellParent.style = "max-width: calc( 15 * 1vw ); border-right: 1px solid #e7e7e7; border-left: 1px solid #e7e7e7;";
        cellParent.style.backgroundColor = globalItemColor;

        cellParent.classList.add("align-left");
        cellParent.classList.add("text-center");
        cellParent.classList.add("text-sm");
        
        fetch('/updatetime/' + id + '/' + targetTime)
        .then(() => {
        //window.location.href = window.location.href;
        })

        var hour = targetTime.split(":")[0];
        var minute = targetTime.split(":")[1];

        // check if minute is undefined
        if (minute == undefined) {
            minute = "00";
        }

        // check if targetTime has am or pm
        if (hour.includes("am") || hour.includes("12pm")) {
            hour = hour.replace("am", "");
            hour = hour.replace("pm", "");
        }
        else if (hour.includes("pm")) {
            hour = hour.replace("pm", "");
            hour = parseInt(hour) + 12;
        }

        var currentCell = document.getElementById(id);

        // get inner div with class name "col-9 m-0 text-sm text-truncate"
        var innerDiv = currentCell.getElementsByClassName("col-9 m-0 text-sm text-truncate")[0];

        // get onclick attribute of inner div
        var onclick = innerDiv.getAttribute("onclick");

        // split based on ,
        var dateTime = onclick.split(",")[2];

        var time = dateTime.split(" ")[2].replace('"', '');

        newOnClick = onclick.replace(time, hour + ":" + minute + ":00");
        innerDiv.setAttribute("onclick", newOnClick);
    }   
}

function unscheduleDrop(event) {
    // this function is called when a scheduled task is dropped over any unscheduled task
    // it means that the scheduled task is being unscheduled

    // get task id
    event.preventDefault();
    var id = event.dataTransfer.getData("text");

    // call unschedule on the task
    fetch('/unschedule/' + id)
    .then(() => {
    window.location.href = window.location.href;
    })
}

function cancelEdit() {

    console.log("cancel edit");

    document.getElementById("note").value  = "";
    document.getElementById("priority").value = "Low";
    document.getElementById("due-time").value = "";
    document.getElementById("time").value = "00:00";
    document.getElementById("repeat").value = "0";
    document.getElementById("noteid").value = "";
    document.getElementById("addnote").innerText  = "Add";
    document.getElementById("addnote").value  = "Add Note";
    document.getElementById("addnote").style.backgroundColor = "#2d89ce";
    document.getElementById("cancelbutton").innerHTML = "";

    var coll = document.getElementById("myCollapse");

    if (coll.classList.contains("show")) {
        var myCollapse = new bootstrap.Collapse(coll);
        myCollapse.hide();
    }
};

function openNav(note_text, note_priority, note_datetime, note_repeat, note_id, details) {
// document.getElementById("mySidenav").style.width = "50%";

//   remove the first charcter from note_text
    //note_text = note_text.substring(2);

    document.getElementById("note").value  = note_text;

    if (arguments[1] == "0") {
        document.getElementById("priority").value = "Low";
    } else if (arguments[1] == "1") {
        document.getElementById("priority").value = "Medium";
    } else if (arguments[1] == "2") {
        document.getElementById("priority").value = "High";
    }

    // split the date and time using java script
    date = note_datetime.split(" ")[0];
    time = note_datetime.split(" ")[1];
    // remove the last charcter from time
    console.log(note_datetime);
    //time = time.substring(0, time.length - 3);
    time = time.substring(0, 5);
    console.log(time);

    document.getElementById("due-time").value = date;
    document.getElementById("time").value = time;
    document.getElementById("repeat").value = note_repeat;
    document.getElementById("noteid").value = note_id;
    document.getElementById("addnote").innerText  = "Save";
    document.getElementById("addnote").value  = "Edit Note";
    document.getElementById("addnote").style.backgroundColor = "#fb6340";
    document.getElementById("note").focus();

    // adding cancel edit button
    if(!document.getElementById('cancel_edit')){
    var btn = document.createElement("BUTTON");
    // btn.innerHTML = '<span class="btn-inner--icon"><i class="bi bi-x-circle-fill"></i></span>';
    btn.innerHTML = 'Cancel';
    btn.className = "col-12 btn btn-primary btn-sm ms-auto px-0 text-nowrap";
    btn.id = "cancel_edit";
    btn.onclick = cancelEdit;
    document.getElementById("cancelbutton").appendChild(btn);
    }

    // expand collapse
    var coll = document.getElementById("myCollapse");
    task_details = document.getElementById("note_detail");
    task_details.style.minHeight = 70 + 'px';   

    if (!coll.classList.contains("show")) {
    var myCollapse = new bootstrap.Collapse(coll);
    myCollapse.show();
    }

    // adding details text and adjust textarea height
    task_details.value = details;
    // task_details.style.overflow = "hidden";
    task_details.style.height = 0 + 'px';
    task_details.style.height = task_details.scrollHeight + 5 + 'px';   
    
}