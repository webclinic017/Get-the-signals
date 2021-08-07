
// Once Dom is created & elements are rendered then run script to show plot.

function getTS(){
    d = new Date();
    datetext = d.toTimeString();
    datetext = datetext.split(' ')[0];
    return datetext;
}

function createToast(graphID, textStatus, errorThrown) {
    datetext = getTS();

    toastNotifsContainer = document.getElementById("toastNotifsContainer");
    toast = document.createElement("div");

    toastAttrs = {
        "class": "toast",
        "role": "alert",
        "aria-live": "assertive",
        "aria-atomic": "true",
        "data-bs-delay": "7000"
    }

    for ([k, v] of Object.entries(toastAttrs)) {
        toast.setAttribute(k, v);
    }

    toastNotifsContainer.appendChild(toast);

    toastHeader = document.createElement("div");
    toast.appendChild(toastHeader);

    toastHeader.className = "toast-header";
    toastHeaderSVG = document.createElementNS('http://www.w3.org/2000/svg', "svg");
    toastHeader.appendChild(toastHeaderSVG);

    svgAttrs = {
        "xmlns": "http://www.w3.org/2000/svg", "width": "16", "height": "16", "fill": "red",
        "class": "bi bi-exclamation-triangle-fill", "viewBox": "0 0 16 16"
    }

    for ([k, v] of Object.entries(svgAttrs)) {
        toastHeaderSVG.setAttribute(k, v);
    }

    svgPath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    svgPath.setAttributeNS(null, "d", "M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z");

    toastHeaderSVG.appendChild(svgPath);

    strg = document.createElement("strong");
    strg.setAttribute("class", "me-auto");
    strg.innerHTML = "Error"

    toastHeader.appendChild(strg);

    sml = document.createElement("small");
    sml.setAttribute("class", "text-muted");
    sml.innerHTML = datetext;

    toastHeader.appendChild(sml);

    btn = document.createElement("button");
    btnAttrs = { "class": "btn-close", "type": "button", "data-bs-dismiss": "toast", "aria-label": "Close" };

    for ([k, v] of Object.entries(btnAttrs)) {
        btn.setAttribute(k, v);
    }

    toastHeader.appendChild(btn);

    toastBody = document.createElement("div");
    toastBody.setAttribute("class", "toast-body");
    toastBody.innerHTML = "Error: " + graphID + "\n" + textStatus + "\n" + errorThrown;
    toast.appendChild(toastBody);

    new bootstrap.Toast(toast).show();

}

function plotGraph(graphID, jsonData) {
    // update the plot, .react is recommended for updating existing plot as it's more efficient than .newPlot
    Plotly.react(graphID, jsonData, { autosize: true });
}


// DRY
function fetchGraphData(apiURL, graphID, spinnerID, refreshBtnID, tsID) {
    // jQuery.get( url [, data ] [, success ] [, dataType ] )
    // $.get({
    //     url: apiURL,
    //     data: null,
    //     success: function (response) {
    //         console.log("response received from server");
    //         plotGraph(graphID, response);
    //         console.log("ploting graph");
    //     },
    //     dataType: "json"
    // });


    $.ajax({
        type: 'GET',
        url: apiURL,
        data: null,
        beforeSend: function () {
            console.log("starting spinner")
            $("#" + spinnerID).addClass("spinner-border");
            $("#" + refreshBtnID).hide();
        },
        success: function (response) {
            console.log("response received from server");
            plotGraph(graphID, JSON.parse(response));
            console.log("ploting graph");
            $("#"+tsID).text(getTS());
        },
        error: function (jqXHR, textStatus, errorThrown) {
            createToast(graphID, textStatus, errorThrown);
            console.log("Error:", graphID, textStatus, errorThrown);

            //errToast = bootstrap.Toast.getOrCreateInstance("#errorToast", {"delay":7000});
            // errToast = new bootstrap.Toast("#errorToast", {"delay":7000})
            // errToast.show();
        },
        complete: function () {
            $("#" + spinnerID).removeClass("spinner-border");
            $("#" + refreshBtnID).show();
        }

    }); //close ajax
}



function fetchSignalChartJsonData() {
    // Graph_2
    console.log("sending request for > signalChart < to server");
    
    fetchGraphData(`http://0.0.0.0:5000/api/fetchSignalChartJsonData?tick=${jQuery('#inputTick').val().trim()}`, "signalChart", "loader_graph2", "refreshBtn_2", "graph_2_TS");

}


// Initial Plots
Plotly.newPlot("signalChart", null, { autosize: true }, { responsive: true }); // Graph 2
fetchSignalChartJsonData(); // inital page load graph 2



















        // window.onresize = function () {
        //     ["barGraph", "signalChart", "temp"].forEach(graphID,
        //         Plotly.relayout(graphID, {
        //             'xaxis.autorange': true,
        //             'yaxis.autorange': true
        //         }));
        // };

        // setInterval(fetchGraphJsonData, 5000); // update every 5 seconds 


        // Understand promise concepts <- Javascript

        // fetch('http://127.0.0.1:5000/fetchGraphJsonData')
        // .then(response => response.json())
        // .then(function(jsonData){
        //     console.log(jsonData);
        //     plotGraph(jsonData);
        // }());

        // function showAllToast() {
        //     // experimental - not debugged completely
        //     var toastElList = [].slice.call(document.querySelectorAll('.toast'));
        //     var toastList = toastElList.map(function (toastEl) {
        //         return new bootstrap.Toast(toastEl)
        //     });
        //     toastList.forEach(toast => toast.show());
        //     console.log(toastList);
        // }


