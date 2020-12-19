

function updateDiscoveryProgress(threadId){
    worker('getDiscoveryProgress/','#discoveryBar', threadId);
}

function updateRetrievalProgress(threadId){
    worker('getRetrievalProgress/','#retrievalBar', threadId)
}

function worker(url, progressBarID, threadId) {
    $.get(url + threadId,function (data) {
        var progress = Number(data);
        if(progress <= 100){
            $(progressBarID).progressbar( "value", progress );
            if(progress !== 100){
                setTimeout(worker, 1000);
            }
        }
    });
}

$(function generateProgressBar(){
    var url = $(location).attr('href'),
    parts = url.split("/"),
    threadId = parts[parts.length - 1];
    updateDiscoveryProgress(threadId);
    updateRetrievalProgress(threadId)
});

