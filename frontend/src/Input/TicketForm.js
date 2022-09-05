import React, {useState} from 'react';
import ImportantButtonWrap from "../shared/ImportantButtonWrap";
import {RequestBox} from "./RequestBox";
import {PaperInputBox} from "./PeriodicalInputs/PaperInputBox";
import {TermInputBox} from "./TermInputBox";
import TextInputBubble from "./TextInputBubble";

function TicketForm(props){
    const [showNoTermsReminder, setShowNoTermsReminder] = useState(false);


    const noTermsReminder = 
        <div>
            <div className='noTermsReminder'>
                <span className='noTermsReminderText'>
                    You have no terms.
                </span>
            </div>
        </div>

    function handleSubmit(e){
        e.preventDefault();
        if (!props.tickets.length){
            setShowTicketReminder(true)
        } else{
            props.onGraphStartClick(e);
        }
    }

    function handleCreateTicketClick(){
        if (!props.selectedTerms || !props.selectedTerms.length){
            setShowNoTermsReminder(true)
        }else{
            setShowTicketReminder(false);
            props.onCreateTicketClick();
        }
    }

    function handleCreateTerm(e){
        e.preventDefault();
        setShowNoTermsReminder(false);
        props.onKeyDown(e);
    }

    return(
        <form
            onSubmit={props.onGraphStartClick}
            className='userInputForm'
        >
            <TermInputBox
                onKeyDown={handleCreateTerm}
                selectedTerms={props.selectedTerms}
                deleteTermBubble={props.deleteTermBubble}
            />
            <br />
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
            <div className='graphWarningBoxBoundary'>
                {showTicketReminder ?
                    noTicketReminder :
                    null
                }
                {showNoTermsReminder ?
                    noTermsReminder :
                    null
                }
            <ImportantButtonWrap>
                <input
                    type='submit'
                    value='Fetch and graph 📊'
                />
            </ImportantButtonWrap>
            </div>


        </form>
    )
}

export default TicketForm;