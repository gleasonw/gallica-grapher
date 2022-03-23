
var url = $(location).attr('href');
var urlParts = url.split("/")
var threadId = urlParts[urlParts.length - 1]

$(document).ready(function() {
    discoveryBarWorker();
});

$(function(){
    $("#discoveryBar").progressbar({
        value: 0,
        complete: function(event, ui){
            getTotalDiscovered();
            retrievalBarWorker();
        }
    });
});

$(function(){
    $("#retrievalBar").progressbar({
        value: 0,
        complete: function(event, ui){
            holdingPatternUntilResultsReady();
        }
    });
});

function discoveryBarWorker() {
    $.getJSON('progress/{0}'.format(threadId), function (data) {
        let discoveryProgress = Number(data['discoveryPercent']);
        $('#discoveryBar').progressbar("value", discoveryProgress);
        if ($('#discoveryBar').progressbar("value") < 100){
            setTimeout(function () {discoveryBarWorker()}, 1000);
        }
    });
}

function retrievalBarWorker() {
     $.getJSON('progress/{0}'.format(threadId), function (data) {
        let retrievalProgress = Number(data['retrievalPercent']);
        $('#retrievalBar').progressbar("value", retrievalProgress);
        if ($('#retrievalBar').progressbar("value") < 100){
            setTimeout(function () {retrievalBarWorker()}, 1000);
        }
    });
}

function getTotalDiscovered(){
    $.get('getDiscoveredResults/{0}'.format(threadId), function(data){
        document.getElementById("numberDiscovered").innerHTML = "Discovering... "+data['numberDiscovered']+" results found.";
    });
}

function getTotalRetrieved(){
    $.get('getNumberRetrievedResults/{0}'.format(threadId), function(data){
        document.getElementById("numberRetrieved").innerHTML = "Retrieved "+data['numberRetrieved']+" non-duplicate results. Generating graph...";
    });
}

function holdingPatternUntilResultsReady(){
    $.getJSON('progress/{0}'.format(threadId), function (data) {
        let state = data['state'];
        console.log(state)
        if (state !== "SUCCESS"){
            console.log("we go again")
            setTimeout(function () {holdingPatternUntilResultsReady()}, 1000);
        }else{
            getTotalRetrieved();
            location.replace('http://127.0.0.1:5000/results/{0}'.format(threadId));
        }
    });
}

String.prototype.format = String.prototype.f = function() {
    var s = this,
        i = arguments.length;

    while (i--) {
        s = s.replace(new RegExp('\\{' + i + '\\}', 'gm'), arguments[i]);
    }
    return s;
};

