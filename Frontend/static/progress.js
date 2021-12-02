threadId = getThreadId()
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
            worker('getRetrievalProgress/', '#retrievalBar')
        }
    });
});

$(function updateDiscoveryProgress(threadId){
    worker('getDiscoveryProgress/','#discoveryBar');
});

function worker(url, progressBarID) {
    $.get(url + threadId,function (data) {
        var progress = Number(data);
        if(progress <= 100){
            $(progressBarID).progressbar( "value", progress );
            if(progress !== 100){
                setTimeout(function() {worker(url, progressBarID)}, 1000);
            }else{
                if(url === 'getRetrievalProgress/'){
                    getRetrieved()
                    window.location.replace('/results/'+threadId)
                }
            }
        }
    });
}

function getThreadId(){
    let url = $(location).attr('href'),
        parts = url.split("/");
    return parts[parts.length - 1];
}

function getDiscovered(){
    $.get('getDiscoveredResults/' + threadId, function(data){
        document.getElementById("numberDiscovered").innerHTML = "Discovering... "+data+" results found.";
    });
}

function getRetrieved(){
    $.get('getNumberRetrievedResults/' + threadId, function(data){
        console.log(data)
        document.getElementById("numberRetrieved").innerHTML = "Retrieved "+data+" non-duplicate results. Generating graph...";
    });
}
