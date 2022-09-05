import React, {useState} from 'react';
import ImportantButtonWrap from "../shared/ImportantButtonWrap";
import {RequestBox} from "./RequestBox";
import {PaperInputBox} from "./PeriodicalInputs/PaperInputBox";
import {TermInputBox} from "./TermInputBox";
import TextInputBubble from "./TextInputBubble";

function TicketForm(props){
    const [showTicketReminder, setShowTicketReminder] = useState(false);
    const [showNoTermsReminder, setShowNoTermsReminder] = useState(false);

    const noTicketReminder =
        <div>
            <div className='noTicketReminder'>
                <span className='noTicketReminderText'>
                    You have no tickets.
                </span>
            </div>
        </div>

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
            onSubmit={handleSubmit}
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
                    <div className='createTicketAndGraphButtonContainer'>
                        <ImportantButtonWrap>
                            <input
                                type='submit'
                                value='Fetch and graph 📊'
                            />
                        </ImportantButtonWrap>
                        <ImportantButtonWrap>
                            <input
                                type='button'
                                value='Add search ticket +'
                                onClick={handleCreateTicketClick}
                            />
                        </ImportantButtonWrap>
                    </div>
                    <RequestBox
                        tickets={props.tickets}
                        onTicketClick={props.onTicketClick}
                    />
            </div>


        </form>
    )
}

export default TicketForm;