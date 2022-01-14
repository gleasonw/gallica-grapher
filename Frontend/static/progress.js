var url = $(location).attr('href');
var urlParts = url.split("/")
var threadId = urlParts[urlParts.length - 1]
console.log(threadId)

$(function(){
    $("#retrievalBar").progressbar({
        value: 0,
    });
});

$(function(){
    $("#discoveryBar").progressbar({
        value: 0,
        complete: function(event, ui){
            getDiscovered()
            worker('progress/{0}'.format(threadId), '#retrievalBar')
        }
    });
});

$(function updateDiscoveryProgress(){
    worker('progress/{0}'.format(threadId),'#discoveryBar');
});

function worker(url) {
    $.getJSON(url, function (data) {
        let discoveryProgress = Number(data['discoveryPercent']);
        let retrievalProgress = Number(data['retrievalPercent']);
        console.log([discoveryProgress, retrievalProgress])
        $('#discoveryBar').progressbar("value", discoveryProgress);
        $('#retrievalBar').progressbar("value", retrievalProgress);
        if(data['state'] === 'SUCCESS' && retrievalProgress >= 100){
            getRetrieved();
            window.location.replace('results');
        }else{
            setTimeout(function () {worker(url)}, 1000);
        }
    });
}

function getDiscovered(){
    $.get('getDiscoveredResults/{0}'.format(threadId), function(data){
        document.getElementById("numberDiscovered").innerHTML = "Discovering... "+data+" results found.";
    });
}

function getRetrieved(){
    $.get('getNumberRetrievedResults/{0}'.format(threadId), function(data){
        document.getElementById("numberRetrieved").innerHTML = "Retrieved "+data+" non-duplicate results. Generating graph...";
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

