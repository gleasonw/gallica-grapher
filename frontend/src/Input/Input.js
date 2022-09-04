import React, {useRef} from "react";
import TicketForm from './TicketForm';
import TicketLabel from "../shared/TicketLabel";
import DecorativeTicket from "../shared/DecorativeTicket";
import ImportantButtonWrap from "../shared/ImportantButtonWrap";
import useData from "../shared/hooks/useData";

function Input(props){
    const exampleBoxRef = useRef(null);
    const [terms, setTerms] = React.useState([]);
    const [paperGroups, setPaperGroups] = React.useState([
        [],
        [],
        []
    ]);
    const [paperArrayDateBoundary, setPaperArrayDateBoundary] = React.useState([1499,2020]);
    const [dateRanges, setDateRanges] = React.useState([
        ['',''],
        ['',''],
        ['','']
    ]);
    const continuousRange = dateRanges[0];
    let queryLowYear = continuousRange[0] === '' ?
        1890 : continuousRange[0];
    let queryHighYear = continuousRange[1] === '' ?
        1920 : continuousRange[1];
    let queryYears = queryLowYear < queryHighYear ?
        [queryLowYear, queryHighYear] : [0,0];
    const queryForContinuousPapers =
        "api/continuousPapers?limit=2000" +
            "&startYear=" + queryYears[0] +
            "&endYear=" + queryYears[1];

    const result = useData(queryForContinuousPapers);
    const continuousPapers = result ? result['paperNameCodes'] : [];

    function makePaperBubble(paper){
        const updatedPapers = paperGroups.slice();
        const userSelectedPapers = updatedPapers[1].slice();
        userSelectedPapers.push(paper)
        updatePaperArrayDateBoundary(userSelectedPapers)
        updatedPapers[1] = userSelectedPapers
        setPaperGroups(updatedPapers)
    }

    function makeTermBubble(term){
        if(term){
            const updatedTerms = terms.slice();
            updatedTerms.push(term)
            setTerms(updatedTerms)
        }
    }

    function deletePaperBubble(bubbleIndex){
        const updatedPaperGroups = paperGroups.slice()
        const bubbleGroup = updatedPaperGroups[1].slice()
        bubbleGroup.splice(bubbleIndex, 1)
        updatePaperArrayDateBoundary(bubbleGroup)
        updatedPaperGroups[1] = bubbleGroup
        setPaperGroups(updatedPaperGroups)
    }

    function deleteTermBubble(bubbleIndex){
        const newTerms = terms.slice()
        newTerms.splice(bubbleIndex, 1)
        setTerms(newTerms)
    }

    function handlePaperDropdownClick(paper){
        makePaperBubble(paper)
    }

    function handleLowDateChange(event, optionIndex){
        const inputLowDate = event.target.value;
        if(isNumeric(inputLowDate) || inputLowDate === '') {
            const updatedRanges = dateRanges.slice()
            const thisRange = updatedRanges[optionIndex].slice()
            thisRange[0] = event.target.value
            updatedRanges[optionIndex] = thisRange
            setDateRanges(updatedRanges)
        }
    }

    function handleHighDateChange(event, optionIndex){
        const inputHighDate = event.target.value;
        if(isNumeric(inputHighDate) || inputHighDate === '') {
            const updatedRanges = dateRanges.slice()
            const thisRange = updatedRanges[optionIndex].slice()
            thisRange[1] = event.target.value
            updatedRanges[optionIndex] = thisRange
            setDateRanges(updatedRanges)
        }
    }

    function handleKeyDown(event){
        event.preventDefault()
        makeTermBubble(event.target.value)
    }

    function handleSeeExamplesClick(){
        exampleBoxRef.current.scrollIntoView({behavior: "smooth"})
    }

    function updatePaperArrayDateBoundary(papers){
        let minYear = 1499
        let maxYear = 2020
        if(papers.length > 0){
            const paperLowYears = papers.map(paper => paper["startDate"])
            const paperHighYears = papers.map(paper => paper["endDate"])
            minYear = Math.min(...paperLowYears)
            maxYear = Math.max(...paperHighYears)
        }
        setPaperArrayDateBoundary([minYear, maxYear])
    }

    function trimUserSelectedRange(paperInputIndex){
        if(paperInputIndex === 1){
            trimUserRangeToActualPaperArrayRange()
        }else{
            minYear
            const dateRange = dateRanges[paperInputIndex]
            if(userRange[0] < minYear || userRange[0] === ''){
                userRange[0] = minYear
            }
            if(userRange[1] > maxYear || userRange[1] === ''){
                userRange[1] = maxYear
            }
        }
        const userRange = dateRanges[1].slice()
        const minYear = paperArrayDateBoundary[0]
        const maxYear = paperArrayDateBoundary[1]
        return userRange
    }

    function isNumeric(str){
        if (typeof str != "string") return false
        return !isNaN(str) && !isNaN(parseFloat(str))
    }

    return (
        <div className='inputBody'>
            <div className='inputUI'>
                <div className="mainTitle">
                    Query the Gallica periodical archive and graph the results.
                </div>
                <TicketForm
                    dateRanges={dateRanges}
                    onLowDateChange={handleLowDateChange}
                    onHighDateChange={handleHighDateChange}
                    onCreateTicketClick={(paperInputIndex) => props.onCreateTicketClick(
                        {
                            'terms': terms,
                            'papersAndCodes': paperInputIndex === 0 ?
                                continuousPapers :
                                paperGroups[paperInputIndex],
                            'dateRange': trimUserSelectedRange(paperInputIndex)
                        }
                    )}
                    onPaperDropItemClick={handlePaperDropdownClick}
                    onKeyDown={handleKeyDown}
                    selectedTerms={terms}
                    paperGroups={paperGroups}
                    deleteTermBubble={deleteTermBubble}
                    deletePaperBubble={deletePaperBubble}
                    minYearPlaceholder={paperArrayDateBoundary[0]}
                    maxYearPlaceholder={paperArrayDateBoundary[1]}
                    onGraphStartClick={props.onInputSubmit}
                    onTicketClick={props.onTicketClick}
                    tickets={props.requestTickets}
                    exampleBoxRef={exampleBoxRef}
                    numContinuousPapers={continuousPapers ?
                        continuousPapers.length :
                        '...'
                    }
                />
                <input
                id='seeExamplesButton'
                type='button'
                onClick={handleSeeExamplesClick}
                value='Or try some examples ↓'
                />
            </div>
        <ExampleBox
            exampleBoxRef={exampleBoxRef}
            onExampleRequestClick={props.onExampleRequestClick}
        />
        </div>


    )

}
//TODO: Cache the examples.
function ExampleBox(props){
    const exampleJSONdata = require('./exampleRequests.json')
    const exampleRequests = exampleJSONdata["requests"]
    return(
        <div
            className='exampleBox'
            ref={props.exampleBoxRef}
        >
            {Object.keys(exampleRequests).map(requestName => (
                <ExampleRequest
                    title={requestName}
                    request={exampleRequests[requestName]}
                    onClick={props.onExampleRequestClick}
                    key={requestName}
                />
            ))}
        </div>

    )
}
function ExampleRequest(props){
    const tickets = props.request["tickets"]
    return(
        <ImportantButtonWrap onClick={() => props.onClick(tickets)}>
            <h1>{props.title}</h1>
            <div className={'exampleRequest'}>
                {tickets.map((ticket, index) => (
                    <DecorativeTicket key={index}>
                        <TicketLabel
                            terms={ticket["terms"]}
                            papers={ticket["papersAndCodes"]}
                            dateRange={ticket["dateRange"]}
                        />
                    </DecorativeTicket>
                ))}

            </div>
        </ImportantButtonWrap>
    )
}

export default Input;