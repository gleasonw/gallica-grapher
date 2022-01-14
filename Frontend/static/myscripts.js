var $inputpapers = $("input#papers");
var $paperBubblesContainer = $('.paperBubblesContainer');
var papers;

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
        if ($("input#yearRange").val() !== "" && !$paperBubblesContainer.children()){
            let paper = $("input#papers").val();
            if (paper === "") {
                $('.form-group#strictness').show();
            } else {
                $('.form-group#strictness').hide();
            }
        } else {
            $('.form-group#strictness').hide();
        }
    })
});
//Now just modify flask to accept the paperBubblesContainer text instead of the input text on a post


$("form#searchStuff").submit(function(event) {
    event.preventDefault()
    let paperChoices = '';
    $('.bubblePaper').each(function() {
        let currentPaper = "{0}%8395%".format($(this).children('.selectedPaper').text());
        paperChoices += currentPaper;
    })
    let userInputs = new FormData();
    userInputs.set('chosenPapers', paperChoices)
    userInputs.set('searchTerm', $("input#searchTerm").val())
    userInputs.set('yearRange', $("input#yearRange").val())
    userInputs.set('strictness', $("input#strictYearRange").val())
    $.ajax({
        type: 'post',
        url: '/home',
        processData: false,
        contentType: false,
        data: userInputs,
        success: function (data, status, request) {
            window.location.replace(request.getResponseHeader('Location'));
        }
    });
});

$inputpapers.one('focus', function(){
    const displayData = async () => {
        const fetchedPapers = await getPapers()
        papers = Object.values(fetchedPapers)
        $inputpapers.trigger('keyup')
    };
    displayData();
});

$inputpapers.on('keyup', (function(){
    if (papers){
        let searchData = $(this).val().toLowerCase();
        const match = papers.filter(paper => {
            return paper.paperName.toLowerCase().includes(searchData)
        })
        let matchedPapers = Object.values(match);
        $(".dropdown").empty();
        for (var i = 0; i < matchedPapers.length; i++){
            $("<div class='paperOptionDrop' id=paper{0}>{1}</div>".format(i, matchedPapers[i].paperName)).appendTo('.dropdown')
        }
    }
}));

$inputpapers.keydown(function(e) {
    if(!$inputpapers.val()){
        var key = e.keyCode;
        if(key === 8){
           $paperBubblesContainer.children().last().remove()
        }
    }
})

$(document).on('click','.paperOptionDrop',function () {
    $inputpapers.val('');
    var thePaper = $(this).text()
    var duplicate = false
    $('.bubblePaper').each(function() {
        var currentPaper = $(this).children('.selectedPaper').text();
        if(currentPaper === thePaper){
            duplicate = true
        }
    })
    if(!duplicate){
        var bubbleDiv = "<div class= 'bubblePaper' id='{0}'>" +
                            "<div class='delete'>X</div>" +
                            "<div class='selectedPaper'>{1}</div>" +
                        "</div>"
        bubbleDiv = bubbleDiv.format(thePaper, thePaper)
        $paperBubblesContainer.append($(bubbleDiv))
    }
    $inputpapers.focus()
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








