function updateProgress(threadId){
    worker();
    function worker() {
        $.get('getProgress/' + threadId,function (data) {
            var progress = Number(data);
            console.log(progress);
            if(progress < 100){
                $( "#progressbar" ).progressbar({
                    value: progress
                });
                setTimeout(worker, 500);
            }
        });
    }
}

$(function generateProgressBar(){
    var url = $(location).attr('href'),
    parts = url.split("/"),
    threadId = parts[parts.length - 1];
    updateProgress(threadId);
});

