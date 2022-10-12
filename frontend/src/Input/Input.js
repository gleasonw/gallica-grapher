import React, {useRef, useState} from "react";
import TicketForm from './TicketForm';
import useData from "../shared/hooks/useData";
import {ExampleBox} from "./ExampleBox";

//TODO: add a reducer
function Input(props){
    const exampleBoxRef = useRef(null);

    const [terms, setTerms] = useState([]);
    const [linkTerm, setLinkTerm] = useState(null);
    const [linkDistance, setLinkDistance] = useState(10);
    const [termInput, setTermInput] = useState('');
    const [userSelectedPapers, setUserSelectedPapers] = useState([]);
    const [selectedPaperInput, setSelectedPaperInput] = useState(0);
    const [customPapersDateRange, setCustomPapersDateRange] = useState(['','']);
    const [continuousDateRange, setContinuousDateRange] = useState(['','']);
    const [fullSearchDateRange, setFullSearchDateRange] = useState(['','']);
    const [fetchType, setFetchType] = useState('all');
    const queryForContinuousPapers = getContinuousPaperQuery();
    const result = useData(queryForContinuousPapers);
    const continuousPapers = result ? result['paperNameCodes'] : [];
    const boundaryYearsForUserPapers = setUserPapersYearBoundary();

    function getContinuousPaperQuery(){
        let queryLowYear = continuousDateRange[0] === '' ?
        1890 : continuousDateRange[0];
        let queryHighYear = continuousDateRange[1] === '' ?
            1920 : continuousDateRange[1];
        return "api/continuousPapers?limit=2000" +
            "&startYear=" + queryLowYear +
            "&endYear=" + queryHighYear;
    }

    function setUserPapersYearBoundary(){
        let minYear = 1499
        let maxYear = 2020
        if(userSelectedPapers.length > 0){
            const paperLowYears = userSelectedPapers.map(paper => paper["startDate"])
            const paperHighYears = userSelectedPapers.map(paper => paper["endDate"])
            minYear = Math.min(...paperLowYears)
            maxYear = Math.max(...paperHighYears)
        }
        return [minYear, maxYear]
    }

    function handleSeeExamplesClick(){
        exampleBoxRef.current.scrollIntoView({behavior: "smooth"})
    }

    function handlePaperInputFocus(index){
        setSelectedPaperInput(index)
    }

    function handleSubmit(event){
        event.preventDefault();
        const currentNumTickets = Object.keys(props.tickets).length
        if(currentNumTickets === 0) {
            const ticket = {
                terms: terms,
                linkTerm: linkTerm,
                linkDistance: linkDistance,
                papersAndCodes: getPapersFor(selectedPaperInput),
                dateRange: getDateRangeFor(selectedPaperInput),
                fetchType: fetchType
            }
            props.onLoadedSubmit(ticket);
        }else{
            props.onUnloadedSubmit();
        }
    }

    function handleKeyDown(event){
        if(event.key === 'ArrowDown'){
            event.preventDefault();
            if(selectedPaperInput < 2){
                setSelectedPaperInput(selectedPaperInput + 1);
            }
        }else if(event.key === 'ArrowUp'){
            event.preventDefault();
            if(selectedPaperInput > 0){
                setSelectedPaperInput(selectedPaperInput - 1);
            }
        }else{

        }
    }

    function handleTermChange(event) {
        const input = event.target.value
        const splitCommaTerms = input.split(',')
        const trimmedTerms = splitCommaTerms.map(term => term.trim())
        setTermInput(input)
        setTerms(trimmedTerms)
    }

    function handlePaperDropdownClick(paper){
        makePaperBubble(paper)
    }

    function handlePaperInputSelectClick(paperInputIndex){
        setSelectedPaperInput(paperInputIndex);
    }

    function handleContinuousLowYearChange(event){
        const inputLowYear = event.target.value
        if(isNumeric(inputLowYear) || inputLowYear === '') {
            const updatedContinousRange = continuousDateRange.slice()
            updatedContinousRange[0] = inputLowYear
            setContinuousDateRange(updatedContinousRange)
        }
    }

    function handleContinuousHighYearChange(event){
        const inputHighYear = event.target.value
        if(isNumeric(inputHighYear) || inputHighYear === '') {
            const updatedContinousRange = continuousDateRange.slice()
            updatedContinousRange[1] = inputHighYear
            setContinuousDateRange(updatedContinousRange)
        }
    }

    function handleCustomLowYearChange(event){
        const inputLowYear = event.target.value
        if(isNumeric(inputLowYear) || inputLowYear === '') {
            const updatedCustomRange = customPapersDateRange.slice()
            updatedCustomRange[0] = inputLowYear
            setCustomPapersDateRange(updatedCustomRange)
        }
    }

    function handleCustomHighYearChange(event){
        const inputHighYear = event.target.value
        if(isNumeric(inputHighYear) || inputHighYear === '') {
            const updatedCustomRange = customPapersDateRange.slice()
            updatedCustomRange[1] = inputHighYear
            setCustomPapersDateRange(updatedCustomRange)
        }
    }

    function handleFullSearchLowYearChange(event){
        const inputLowYear = event.target.value
        if(isNumeric(inputLowYear) || inputLowYear === '') {
            const updatedFullSearchRange = fullSearchDateRange.slice()
            updatedFullSearchRange[0] = inputLowYear
            setFullSearchDateRange(updatedFullSearchRange)
        }
    }

    function handleFullSearchHighYearChange(event){
        const inputHighYear = event.target.value
        if(isNumeric(inputHighYear) || inputHighYear === '') {
            const updatedFullSearchRange = fullSearchDateRange.slice()
            updatedFullSearchRange[1] = inputHighYear
            setFullSearchDateRange(updatedFullSearchRange)
        }
    }

    function handleCreateTicketClick(){
        props.onCreateTicketClick({
            terms: terms,
            linkTerm: linkTerm,
            linkDistance: linkDistance,
            papersAndCodes: getPapersFor(selectedPaperInput),
            dateRange: getDateRangeFor(selectedPaperInput),
            fetchType: fetchType
        });
        setTermInput('');
        setTerms([]);
        setContinuousDateRange(['','']);
        setCustomPapersDateRange(['','']);
        setFullSearchDateRange(['','']);
        setUserSelectedPapers([]);
        setLinkDistance(10);
        setLinkTerm('');
        setFetchType('all');
    }


    function deleteTermBubble(bubbleIndex){
        const newTerms = terms.slice()
        newTerms.splice(bubbleIndex, 1)
        setTerms(newTerms)
    }

    function makePaperBubble(paper){
        const updatedPapers = userSelectedPapers.slice();
        updatedPapers.push(paper)
        setUserSelectedPapers(updatedPapers)
    }

    function deletePaperBubble(bubbleIndex){
        const updatedPapers = userSelectedPapers.slice();
        updatedPapers.splice(bubbleIndex, 1)
        setUserSelectedPapers(updatedPapers)
    }

    function getPapersFor(paperInputIndex){
        if(paperInputIndex === 0){
            return continuousPapers
        }else if(paperInputIndex === 1){
            return userSelectedPapers
        }else if(paperInputIndex === 2){
            return []
        }else{
            throw Error(`Unexpected paper index: ${paperInputIndex}`)
        }
    }

    function getDateRangeFor(paperInputIndex){
        if(paperInputIndex === 0){
            return assignNullRangeValuesToPlaceholder(
                continuousDateRange,
                1890,
                1920
                )
        }else if(paperInputIndex === 1){
            let trimmedRange = trimCustomPaperRangeToActualPaperRange()
            const lowYearDefault = boundaryYearsForUserPapers[0]
            const highYearDefault = boundaryYearsForUserPapers[1]
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
            throw Error(`Unexpected paper index: ${paperInputIndex}`)
        }
    }

    function trimCustomPaperRangeToActualPaperRange(){
        const userRange = customPapersDateRange
        const minYear = boundaryYearsForUserPapers[0]
        const maxYear = boundaryYearsForUserPapers[1]
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
        }
        if (range[1] === '') {
            range[1] =highDefault
        }
        return range
    }

    function isNumeric(str){
        if (typeof str != "string") return false
        return !isNaN(str) && !isNaN(parseFloat(str))
    }

    return (
        <div className='inputBody' onKeyDown={handleKeyDown}>
            <div className='inputUI'>
                <div className="mainTitle">
                    Graph word occurrences in archived French periodicals.
                </div>
                <TicketForm
                    dateRanges = {[
                        continuousDateRange,
                        customPapersDateRange,
                        fullSearchDateRange
                    ]}
                    dateRangeHandlers = {[
                        [
                            handleContinuousLowYearChange,
                            handleContinuousHighYearChange
                        ],
                        [
                            handleCustomLowYearChange,
                            handleCustomHighYearChange
                        ],
                        [
                            handleFullSearchLowYearChange,
                            handleFullSearchHighYearChange
                        ]
                    ]}
                    onCreateTicketClick={handleCreateTicketClick}
                    onPaperDropItemClick={handlePaperDropdownClick}
                    terms={terms}
                    termInput={termInput}
                    linkTerm={linkTerm}
                    linkDistance={linkDistance}
                    onLinkTermChange={(e) => setLinkTerm(e.target.value)}
                    onLinkDistanceChange={(e) => setLinkDistance(e.target.value)}
                    handleTermChange={handleTermChange}
                    userSelectedPapers={userSelectedPapers}
                    deleteTermBubble={deleteTermBubble}
                    deletePaperBubble={deletePaperBubble}
                    boundaryYearsForUserPapers={boundaryYearsForUserPapers}
                    onSubmit={handleSubmit}
                    onGraphStartClick={handleSubmit}
                    onTicketClick={props.onTicketClick}
                    tickets={props.tickets}
                    exampleBoxRef={exampleBoxRef}
                    onPaperInputClick={handlePaperInputSelectClick}
                    selectedPaperInput={selectedPaperInput}
                    numContinuousPapers={continuousPapers ?
                        continuousPapers.length :
                        '...'
                    }
                    requestBoxRef={props.requestBoxRef}
                    onPaperInputFocus={handlePaperInputFocus}
                />
                <input
                    id='seeExamplesButton'
                    type='button'
                    aria-label='Scroll to examples'
                    onClick={handleSeeExamplesClick}
                    value='Or view an example ↓'
                />
            </div>
        <ExampleBox
            exampleBoxRef={exampleBoxRef}
            onExampleRequestClick={props.onExampleRequestClick}
        />
        </div>


    )

}

export default Input;