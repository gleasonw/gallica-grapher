threadId = getThreadId()
$(function(){
    $("#retrievalBar").progressbar({
        value: 0
    });
});

$(function(){
    $("#discoveryBar").progressbar({
        value: 0,
        complete: function(event, ui){
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
        console.log(progress)
        if(progress <= 100){
            $(progressBarID).progressbar( "value", progress );
            if(progress !== 100){
                setTimeout(function() {worker(url, progressBarID)}, 1000);
            }else{
                if(url === 'getRetrievalProgress/'){
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
