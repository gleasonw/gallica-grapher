import React, {useState} from 'react';
import ImportantButtonWrap from "../shared/ImportantButtonWrap";
import {RequestBox} from "./RequestBox";
import {PaperInputBox} from "./PeriodicalInputs/PaperInputBox";
import {TermInputBox} from "./TermInputBox";

function TicketForm(props){
    const [selectedPaperInput, setSelectedPaperInput] = useState(1);
    const [showTicketReminder, setShowTicketReminder] = useState(false);
    const noTicketReminder =
        <div>
            <div className='noTicketReminder'>
                <span className='noTicketReminderText'>
                    You have no tickets.
                </span>
            </div>
        </div>

    function handleSubmit(e){
        e.preventDefault();
        if (props.tickets && props.tickets.length > 0){
            props.onGraphStartClick(e);
        }else{
            setShowTicketReminder(true);
        }
    }

    function handleCreateTicketClick(paperInputIndex){
        setShowTicketReminder(false);
        props.onCreateTicketClick(selectedPaperInput);
    }

    function handlePaperInputSelectClick(paperInputIndex){
        setSelectedPaperInput(paperInputIndex);
    }

    return(
        <form
            onSubmit={handleSubmit}
            className='userInputForm'
        >
            <TermInputBox
                onKeyDown={props.onKeyDown}
                selectedTerms={props.selectedTerms}
                deleteTermBubble={props.deleteTermBubble}
            />
            <br />
            <PaperInputBox
                onClick={props.onPaperDropItemClick}
                onPaperInputSelectClick={handlePaperInputSelectClick}
                paperGroups={props.paperGroups}
                deletePaperBubble={props.deletePaperBubble}
                dateRanges={props.dateRanges}
                onLowDateChange={props.onLowDateChange}
                onHighDateChange={props.onHighDateChange}
                selectedPaperInput={selectedPaperInput}
                numContinuousPapers={props.numContinuousPapers}
            />
            <div className='graphWarningBoxBoundary'>
                {showTicketReminder && props.tickets.length === 0 ?
                    noTicketReminder :
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