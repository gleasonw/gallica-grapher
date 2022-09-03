import React, {useState} from 'react';
import ImportantButtonWrap from "../shared/ImportantButtonWrap";
import {RequestBox} from "./RequestBox";
import {PaperInputBox} from "./PaperInputBox";
import {DateInputBox} from "./DateInputBox";
import {TermInputBox} from "./TermInputBox";

function TicketForm(props){
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

    function handleCreateTicketClick(){
        setShowTicketReminder(false);
        props.onCreateTicketClick();
    }

    return(
        <form
            onSubmit={handleSubmit}
            className='userInputForm'
        >
            <TermInputBox
                onChange={props.onTermChange}
                onKeyDown={props.onKeyDown}
                selectedTerms={props.selectedTerms}
                deleteTermBubble={props.deleteTermBubble}
            />
            <br />
            <PaperInputBox
                onClick={props.onPaperDropItemClick}
                onChange={props.onPaperChange}
                selectedPapers={props.selectedPapers}
                deletePaperBubble={props.deletePaperBubble}
                lowYear={props.lowYearValue ? props.lowYearValue : props.minYearPlaceholder}
                highYear={props.highYearValue ? props.highYearValue : props.maxYearPlaceholder}
            />
            <br />
            <DateInputBox
                onLowDateChange={props.onLowDateChange}
                onHighDateChange={props.onHighDateChange}
                minYearPlaceholder={props.minYearPlaceholder}
                maxYearPlaceholder={props.maxYearPlaceholder}
                lowYear={props.lowYearValue}
                highYear={props.highYearValue}
            />
            <div className='graphWarningBoxBoundary'>
                {showTicketReminder && props.tickets.length === 0 ? noTicketReminder : null}
                <div className='createTicketAndGraphButtonContainer'>
                    <ImportantButtonWrap>
                        <input
                            type='button'
                            value='Add series +'
                            onClick={handleCreateTicketClick}
                        />
                    </ImportantButtonWrap>
                    <ImportantButtonWrap>
                        <input
                            type='submit'
                            value='Fetch and graph 📊'
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