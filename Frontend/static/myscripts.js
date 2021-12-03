
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

var $inputpapers = $("input#papers");
var $paperBubblesContainer = $('.paperBubblesContainer');
var papers;

$inputpapers.one('click', function(){
    const displayData = async () => {
        const fetchedPapers = await getPapers()
        papers = Object.values(fetchedPapers)
        console.log(papers)
    };
    displayData();
});

$inputpapers.keyup(function(){
    let searchData = $(this).val().toLowerCase();
    const match = papers.filter(paper => {
        return paper.paperName.toLowerCase().includes(searchData)
    })
    let matchedPapers = Object.values(match);
    $(".dropdown").empty();
    for (var i = 0; i < matchedPapers.length; i++){
        $("<div class='paperOptionDrop' id=paper{0}>{1}</div>".format(i, matchedPapers[i].paperName)).appendTo('.dropdown')
    }
});

$inputpapers.keydown(function(e) {
    if(!$inputpapers.val()){
        var key = e.keyCode;
        console.log(key)
        if(key === 8){
           $paperBubblesContainer.children().last().remove()
        }
    }
})

$(document).on('click','.paperOptionDrop',function () {
    var thePaper = $(this).text()
    var bubbleDiv = "<div class= 'bubblePaper' id='{0}'>{1}</div>".format(thePaper, thePaper)
    $paperBubblesContainer.append($(bubbleDiv))
});

$(document).on('click','.bubblePaper',function () {
    $(this).remove()
});

const getPapers = async () => {
    const papersResponse = await fetch('/papers');
    return await papersResponse.json()
};

String.prototype.format = String.prototype.f = function() {
    var s = this,
        i = arguments.length;

    while (i--) {
        s = s.replace(new RegExp('\\{' + i + '\\}', 'gm'), arguments[i]);
    }
    return s;
};








