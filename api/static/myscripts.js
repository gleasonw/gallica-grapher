var $inputpapers = $("input#papers");
var $inputTerms = $("input#searchTerm");
var $inputrange = $("input#yearRange");
var $termBubblesContainer= $(".termBubblesContainer");
var $paperInputAndDropdown = $(".paperInputAndDropdown")
var $dropdown = $('.dropdown');
var $strictnessoption = $('.form-group#strictnesschecker')
var $splitPapersOption = $('.form-group#papergraphoptions')
var $splitTermsOption = $('.form-group#termGraphOptions')
var $paperBubblesContainer = $('.paperBubblesContainer');
var papers;
//TODO: Year range slider with paper heatmap!
//TODO: Send papers and terms in array?
$("form#searchStuff").submit(function(event) {
    event.preventDefault()
    let paperChoices = [];
    let termChoices = [];
    $('.selectedPaper').each(function() {
        console.log($(this).text())
        paperChoices.push($(this).text());
    })
    $('.selectedTerm').each(function() {
        console.log($(this).text())
        termChoices.push($(this).text());
    })
    let userInputs = new FormData();
    userInputs.append('papers', JSON.stringify(paperChoices))
    userInputs.append('searchTerm', JSON.stringify(termChoices))
    userInputs.append('yearRange', $("input#yearRange").val())
    userInputs.append('strictness', $("input#strictness").is(":checked"))
    userInputs.append('splitpapers', $("input#grouppapers").is(":checked"))
    userInputs.append('splitterms', $("input#groupTerms").is(":checked"))
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
//TODO: Timer after keyup -- send single query, don't get all the papers! Speed up paper dropdown selection, add search notification (spinny thingy?)
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

$inputpapers.focusin(function(){
    $dropdown.show()
})

$inputrange.on("keyup", function(){
    strictnessButtonHideShowCheck()
});

//Close dropdown on click out, also check if we should be showing buttons
$(document).click(function(event) {
    var $target = $(event.target);
    if(!$target.closest($paperInputAndDropdown).length && $dropdown.is(":visible")) {
        $inputpapers.val('');
        $dropdown.hide();
    }
    strictnessButtonHideShowCheck()
    paperTrendButtonHideShowCheck()
    termTrendButtonHideShowCheck()
});

function strictnessButtonHideShowCheck(){
      //Remove strictness option if papers have been selected... better way to check this?
    if (Object.keys($paperBubblesContainer.children()).length > 2 || !$inputrange.val() || Object.keys($termBubblesContainer.children()).length <= 2){
        $strictnessoption.hide();
    }else{
        if ($("input#yearRange").val() && Object.keys($termBubblesContainer.children()).length > 2){
           $strictnessoption.css("display","flex");
        }
    }
}

function paperTrendButtonHideShowCheck(){
    //Remove paper trend line option if one or no papers selected, else show
    if (Object.keys($paperBubblesContainer.children()).length > 3){
        $splitPapersOption.css("display","flex");
    }else{
        $splitPapersOption.hide()
    }
}

function termTrendButtonHideShowCheck(){
    //Remove term split trend line option if one or no terms selected, else show
    if (Object.keys($termBubblesContainer.children()).length > 3){
        $splitTermsOption.css("display","flex");
    }else{
        $splitTermsOption.hide();
    }
}

$inputTerms.focusout(function(e) {
    createTermBubbles()
})

function createTermBubbles(){
    let userTerm = $inputTerms.val();
    if (userTerm){
        $inputTerms.val('');
        var duplicate = false;
        $('.bubbleTerm').each(function() {
            var currentTerm = $(this).children('.selectedTerm').text();
            if(currentTerm === userTerm){
                duplicate = true
            }
        })
        if(!duplicate){
            let bubbleDiv = "<div class= 'bubbleTerm' id='"+userTerm+"'>" +
                "<div class='delete'>X</div>" +
                "<div class='selectedTerm'>"+userTerm+"</div>" +
                "</div>";
            $termBubblesContainer.append($(bubbleDiv))
        }
    }
}

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
        let bubbleDiv = "<div class= 'bubblePaper' id='{0}'>" +
            "<div class='delete'>X</div>" +
            "<div class='selectedPaper'>{1}</div>" +
            "</div>";
        bubbleDiv = bubbleDiv.format(thePaper, thePaper)
        $paperBubblesContainer.append($(bubbleDiv))
    }
    $inputpapers.focus()
});

$(document).on('click','.bubblePaper',function () {
    $(this).remove()
});

$(document).on('click','.bubbleTerm',function () {
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








