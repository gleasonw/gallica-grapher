import TicketLabel from "../shared/TicketLabel";
import React from "react";
import DecorativeTicket from "../shared/DecorativeTicket";
import styled from 'styled-components';
import LesserButton from "../shared/LesserButton";
import RemoveCircleIcon from '@mui/icons-material/RemoveCircle';
import SmallIconStyle from "../shared/SmallIconStyle";

export function RequestBox(props) {
    if(Object.keys(props.tickets).length > 0){
        return (
        Object.keys(props.tickets).map(ticketID => (
            <DecorativeTicket key={ticketID}>
                <SmallIconStyle onClick={() => props.onTicketClick(ticketID)}>
                    <RemoveCircleIcon/>
                </SmallIconStyle>
                <RequestTicket
                    ticket={props.tickets[ticketID]}
                />
            </DecorativeTicket>
            ))
        )
    }else{
        return(
        <LesserButton onClick={props.onCreateTicketClick}>
            Add a ticket to search
        </LesserButton>
            )
    }
}

export const StyledRequestBox = styled(RequestBox)`
    display: flex;
    flex-direction: row;
    transition: all 150ms;
    
`;

function RequestTicket(props) {
    const terms = props.ticket['terms']
    const papers = props.ticket['papersAndCodes']
    const dateRange = props.ticket['dateRange']
    return (
        <button
            type="button"
            onClick={props.onClick}
        >
            <div className="ticket">
                <TicketLabel
                    terms={terms}
                    papers={papers}
                    dateRange={dateRange}
                />
            </div>
        </button>
    );
}

