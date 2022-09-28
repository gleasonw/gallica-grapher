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
    return(
        <DecorativeTicket
            borderRadius={borderRadius}
            maxWidth={props.maxWidth}
            isMutable={props.isMutable}
        >
            <SeriesColorBubble color={props.color}/>
            {props.actionIcon}
            <TicketLabel
                terms={props.ticket['terms']}
                papers={props.ticket['papersAndCodes']}
                dateRange={props.ticket['dateRange']}
                compact={true}
            />
        </DecorativeTicket>
    )
}