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
        if ((!props.tickets || props.tickets.length === 0)
            &&
            (!props.terms || props.terms.length === 0))
        {
            setShowNoTermsReminder(true)
        } else{
            props.onSubmit(e);
        }
    }

    return(
        <form
            onSubmit={props.onGraphStartClick}
            className='userInputForm'
        >
            <label>Graph this term:</label>
            <TermInputBox
                onEnterPress={handleSubmit}
                selectedTerms={props.selectedTerms}
                deleteTermBubble={props.deleteTermBubble}
                termInput={props.termInput}
                handleTermChange={props.handleTermChange}
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
            />
            <br />
            <RequestBoxAndFetchButtonWrap>
                <StyledRequestBox
                    tickets={props.tickets}
                    onTicketClick={props.onTicketClick}
                    className={'requestBox'}
                    onCreateTicketClick={props.onCreateTicketClick}
                />
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