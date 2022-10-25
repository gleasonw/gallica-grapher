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
    const [selectedPaperInput, setSelectedPaperInput] = useState(2);
    const queryForContinuousPapers = getContinuousPaperQuery();
    const result = useData(queryForContinuousPapers);
    const continuousPapers = result ? result['paperNameCodes'] : [];
    const boundaryYearsForUserPapers = setUserPapersYearBoundary();

    function getContinuousPaperQuery(){
        return "api/continuousPapers?limit=2000" +
            "&startDate=" + props.startDate +
            "&endDate=" + props.endDate;
    }

    function setUserPapersYearBoundary(){
        if(userSelectedPapers.length > 0) {
            const paperLowYears = userSelectedPapers.map(paper => paper["startDate"])
            const paperHighYears = userSelectedPapers.map(paper => paper["endDate"])
            const minYear = Math.min(...paperLowYears)
            const maxYear = Math.max(...paperHighYears)
            return [minYear, maxYear]
        }
    }

    function handleSubmit(event){
        event.preventDefault();
        const currentNumTickets = Object.keys(props.tickets).length
        if(currentNumTickets === 0) {
            const ticket = makeTicketFromState();
            props.onLoadedSubmit(ticket);
        }else{
            props.onUnloadedSubmit();
        }
    }

    function makeTicketFromState(){
        return {
            terms: terms,
            linkTerm: linkTerm,
            linkDistance: linkDistance,
            papersAndCodes: getPapersFor(selectedPaperInput),
            startDate: props.startDate,
            endDate: props.endDate,
        }
    }

    function handleTermChange(event) {
        const input = event.target.value
        const splitCommaTerms = input.split(',')
        const trimmedTerms = splitCommaTerms.map(term => term.trim())
        setTermInput(input)
        setTerms(trimmedTerms)
    }

    function handleCreateTicketClick(){
        props.onCreateTicketClick(makeTicketFromState());
        setTermInput('');
        setTerms([]);
        setUserSelectedPapers([]);
        setLinkDistance(10);
        setLinkTerm('');
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

    return (
        <div className='inputBody'>
            <div className='inputUI'>
                <div className="mainTitle">
                    Graph word occurrences in archived French periodicals.
                </div>
                <TicketForm
                    startDate={props.startDate}
                    endDate={props.endDate}
                    onstartDateChange={props.onstartDateChange}
                    onendDateChange={props.onendDateChange}
                    onCreateTicketClick={handleCreateTicketClick}
                    onPaperDropItemClick={(paper) => makePaperBubble(paper)}
                    onPaperInputFocus={(i) => setSelectedPaperInput(i)}
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
                    onPaperInputClick={(i) => setSelectedPaperInput(i)}
                    selectedPaperInput={selectedPaperInput}
                    selectedSearchType={props.selectedSearchType}
                    onSearchTypeClick={(selectIndex) => props.onSearchTypeChange(selectIndex)}
                    numContinuousPapers={continuousPapers ?
                        continuousPapers.length :
                        '...'
                    }
                    requestBoxRef={props.requestBoxRef}
                />
                <input
                    id='seeExamplesButton'
                    type='button'
                    aria-label='Scroll to examples'
                    onClick={() => exampleBoxRef.current.scrollIntoView(
                        {behavior: "smooth"})
                    }
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