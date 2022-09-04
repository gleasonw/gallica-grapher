import React, {useRef, useState} from "react";
import TicketForm from './TicketForm';
import TicketLabel from "../shared/TicketLabel";
import DecorativeTicket from "../shared/DecorativeTicket";
import ImportantButtonWrap from "../shared/ImportantButtonWrap";
import useData from "../shared/hooks/useData";

function Input(props){
    const exampleBoxRef = useRef(null);
    const [terms, setTerms] = useState([]);
    const [userSelectedPapers, setUserSelectedPapers] = useState([]);
    const [autoContinuousPapers, setAutoContinuousPapers] = useState([]);
    const [customPapersDateRange, setCustomPapersDateRange] = useState(['','']);
    const [autoContinuousDateRange, setAutoContinuousDateRange] = useState(['','']);
    const [fullSearchDateRange, setFullSearchDateRange] = useState(['',''])
    const [paperGroups, setPaperGroups] = useState([
        [],
        [],
        []
    ]);
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
    const lowestStartHighestEndYearsOfUserPapers = setPaperArrayDateBoundary();

    const result = useData(queryForContinuousPapers);
    const continuousPapers = result ? result['paperNameCodes'] : [];

    
    function makeTermBubble(term){
        if(term){
            const updatedTerms = terms.slice();
            updatedTerms.push(term)
            setTerms(updatedTerms)
        }
    }

    function deleteTermBubble(bubbleIndex){
        const newTerms = terms.slice()
        newTerms.splice(bubbleIndex, 1)
        setTerms(newTerms)
    }
    
    function makePaperBubble(paper){
        const updatedPapers = userSelectedPapers.slice();
        updatedPapers.push(paper)
        setPaperArrayDateBoundary(updatedPapers)
        setUserSelectedPapers(updatedPapers)
    }

    function deletePaperBubble(bubbleIndex){
        const updatedPapers = userSelectedPapers.slice();
        updatedPapers.splice(bubbleIndex, 1)
        setPaperArrayDateBoundary(updatedPapers)
        setUserSelectedPapers(updatedPapers)
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

    function setPaperArrayDateBoundary(){
        const userPaperChoices = paperGroups[1]
        let minYear = 1499
        let maxYear = 2020
        if(userPaperChoices.length > 0){
            const paperLowYears = userPaperChoices.map(paper => paper["startDate"])
            const paperHighYears = userPaperChoices.map(paper => paper["endDate"])
            minYear = Math.min(...paperLowYears)
            maxYear = Math.max(...paperHighYears)
        }
        return [minYear, maxYear]
    }

    function trimUserSelectedRange(paperInputIndex){
        if(paperInputIndex === 0){
            return assignNullRangeValuesToPlaceholder(
                customPapersDateRange, 
                1890, 
                2020
                )
        }else if(paperInputIndex === 1){
            let trimmedRange = trimCustomPaperRangeToActualPaperRange()
            const lowYearDefault = lowestStartHighestEndYearsOfUserPapers[0]
            const highYearDefault = lowestStartHighestEndYearsOfUserPapers[1]
            return assignNullRangeValuesToPlaceholder(
                trimmedRange, 
                lowYearDefault, 
                highYearDefault
            )
        }else if(paperInputIndex === 2){
            return assignNullRangeValuesToPlaceholder(
                fullSearchDateRange,
                1499,
                2020
            )
        }else{
            throw `Unexpected paper index: ${paperInputIndex}`
        }
    }

    function trimCustomPaperRangeToActualPaperRange(){
        const userRange = customPapersDateRange
        const minYear = lowestStartHighestEndYearsOfUserPapers[0]
        const maxYear = lowestStartHighestEndYearsOfUserPapers[1]
        if(userRange[0] < minYear){
            userRange[0] = minYear
        }
        if(userRange[1] > maxYear){
            userRange[1] = maxYear
        }
        return userRange
    }

    function assignNullRangeValuesToPlaceholder(range, lowDefault, highDefault){
        if (range[0] === '') {
            range[0] = lowDefault
        if (range[1] === '') {
            range[1] =highDefault
        }
        return range
    }

    function getPapersFor(paperInputIndex){
        if(paperInputIndex === 0){
            return continuousPapers
        }else if(paperInputIndex === 1){
            return userSelectedPapers
        }else if(paperInputIndex === 2){
            return []
        }else{
            throw `Unexpected paper index: ${paperInputIndex}`
        }
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
                            'papersAndCodes': getPapersFor(paperInputIndex),
                            'dateRange': trimUserSelectedRange(paperInputIndex)
                        }
                    )}
                    onPaperDropItemClick={handlePaperDropdownClick}
                    onKeyDown={handleKeyDown}
                    selectedTerms={terms}
                    paperGroups={paperGroups}
                    deleteTermBubble={deleteTermBubble}
                    deletePaperBubble={deletePaperBubble}
                    minYearPlaceholder={lowestStartHighestEndYearsOfUserPapers[0]}
                    maxYearPlaceholder={lowestStartHighestEndYearsOfUserPapers[1]}
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
                            userPaperChoices={ticket["papersAndCodes"]}
                            dateRange={ticket["dateRange"]}
                        />
                    </DecorativeTicket>
                ))}

            </div>
        </ImportantButtonWrap>
    )
}

export default Input;