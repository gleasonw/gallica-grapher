import React, {useState} from 'react';
import ImportantButtonWrap from "../shared/ImportantButtonWrap";
import {StyledRequestBox} from "./RequestBox";
import {PaperInputBox} from "./PeriodicalInputs/PaperInputBox";
import {TermInputBox} from "./TermInputBox";
import RequestBoxAndFetchButtonWrap from "./RequestBoxAndFetchButtonWrap";

function TicketForm(props){
    const [showNoTermsReminder, setShowNoTermsReminder] = useState(false);

    function handleSubmit(e){
        e.preventDefault();
        if ((!props.tickets || Object.keys(props.tickets).length === 0)
            &&
            (props.termInput === ''))
        {
            setShowNoTermsReminder(true)
        }else{
            props.onSubmit(e);
        }
    }

    function handleCreateTicketClick(){
        if(props.termInput !== '') {
            props.onCreateTicketClick();
        }else{
            setShowNoTermsReminder(true);
        }
    }

    function handleTermChange(e){
        setShowNoTermsReminder(false);
        props.handleTermChange(e);
    }

    return(
        <form
            onSubmit={handleSubmit}
            className='userInputForm'
        >
            <label>Graph this term:</label>
            <TermInputBox
                onEnterPress={handleSubmit}
                selectedTerms={props.selectedTerms}
                deleteTermBubble={props.deleteTermBubble}
                termInput={props.termInput}
                handleTermChange={handleTermChange}
                noTermsReminder={showNoTermsReminder}
            />
            <br />
            <label>in...</label>
            <PaperInputBox
                onClick={props.onPaperDropItemClick}
                deletePaperBubble={props.deletePaperBubble}
                dateRanges={props.dateRanges}
                dateRangeHandlers={props.dateRangeHandlers}
                onPaperInputSelectClick={props.onPaperInputClick}
                selectedPaperInput={props.selectedPaperInput}
                numContinuousPapers={props.numContinuousPapers}
                userSelectedPapers={props.userSelectedPapers}
                boundaryYearsForUserPapers={props.boundaryYearsForUserPapers}
                onFocus={props.onPaperInputFocus}
            />
            <div ref={props.requestBoxRef}>
            <StyledRequestBox
                tickets={props.tickets}
                onTicketClick={props.onTicketClick}
                className={'requestBox'}
                onCreateTicketClick={handleCreateTicketClick}
            />
            </div>
            <br />
            <RequestBoxAndFetchButtonWrap>
                <ImportantButtonWrap>
                    <input
                        type='submit'
                        value='Fetch and graph 📊'
                    />
                </ImportantButtonWrap>
            </RequestBoxAndFetchButtonWrap>
        </form>
    )
}


export default TicketForm;