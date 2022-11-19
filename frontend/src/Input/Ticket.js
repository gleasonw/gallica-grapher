import DecorativeTicket from "../shared/DecorativeTicket";
import TicketLabel from "../shared/TicketLabel";
import React from "react";
import SeriesColorBubble from "../shared/SeriesColorBubble";

export default function Ticket(props){
    let borderRadius = [0, 0, 0, 0];
    if(props.firstInRow){
        borderRadius[3] = '10px';
        !props.isMutable && (borderRadius[0] = '10px');
    }if(props.lastInRow){
        borderRadius[2] = '10px';
        !props.isMutable && (borderRadius[1] = '10px');
    }
    borderRadius = borderRadius.join(' ');
    let ticketIsMismatched;
    if (props.mismatchedDataOrigin) {
        const [mismatchPresent, attemptedInput] = props.mismatchedDataOrigin;
        ticketIsMismatched = mismatchPresent && attemptedInput !== props.ticket.dataFromPyllica
    }else{
        ticketIsMismatched = false;
    }

    return(
        <DecorativeTicket
            borderRadius={borderRadius}
            maxWidth={props.maxWidth}
            isMutable={props.isMutable}
            ticketIsMismatched={ticketIsMismatched}
        >
            <SeriesColorBubble color={props.color}/>
            {props.actionIcon}
            <TicketLabel
                terms={props.ticket['terms']}
                papers={props.ticket['papersAndCodes']}
                startDate={props.ticket['startDate']}
                endDate={props.ticket['endDate']}
                linkTerm={props.ticket['linkTerm']}
                linkDistance={props.ticket['linkDistance']}
                compact
            />
        </DecorativeTicket>
    )
}