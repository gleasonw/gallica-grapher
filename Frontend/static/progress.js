

function updateProgress(threadId){
    worker();
    function worker() {
        $.get('getProgress/' + threadId,function (data) {
            var progress = Number(data);
            console.log(progress)
            if(progress <= 100){
                $( "#progressBar" ).progressbar( "value", progress );
            }
            setTimeout(worker, 1000);
        });
    }
}

$(function generateProgressBar(){
    var url = $(location).attr('href'),
    parts = url.split("/"),
    threadId = parts[parts.length - 1];
    updateProgress(threadId);
});

