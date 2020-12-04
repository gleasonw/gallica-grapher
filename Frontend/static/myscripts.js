
$(function() {
    $('#hidden-form-group').show();
    $('#graphType').on("input",function(){
        if(['freqPoly','stackedBar','bar'].indexOf($('#graphType').val()) >= 0) {
            $('#hidden-form-group').show();
        } else {
            $('#hidden-form-group').hide();
        }
    });
});

$(function strictnessChecker(){
    $('.form-group#strictness').hide();
    $("input#yearRange,input#papers").on("keyup", function(){
        if ($("input#yearRange").val() !== "") {
            let paper = $("input#papers").val();
            if (paper === "" || paper === "all") {
                $('.form-group#strictness').show();
            } else {
                $('.form-group#strictness').hide();
            }
        } else {
            $('.form-group#strictness').hide();
        }
    })
});


$(function updateProgress(){
    var url = $(location).attr('href'),
        parts = url.split("/"),
        task_id = parts[parts.length-1]
    function worker(){
        $.get('progress/' + task_id, function(data){
            if (progress < 100){
                $('#progressBar').progressbar({value:progress})
                setTimeout(worker,1000)
            }
        })
    }
});






// let i = 0;
//
// function move() {
//   if (i === 0) {
//     i = 1;
//     var elem = document.getElementById("establishResultsBar");
//     var width = 1;
//     var id = setInterval(frame, 10);
//     function frame() {
//       if (width >= 100) {
//         clearInterval(id);
//         i = 0;
//       } else {
//         width++;
//         elem.style.width = width + "%";
//       }
//     }
//   }
// }