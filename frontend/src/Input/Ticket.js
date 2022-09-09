import DecorativeTicket from "../shared/DecorativeTicket";
import SmallIconStyle from "../shared/SmallIconStyle";
import RemoveCircleIcon from "@mui/icons-material/RemoveCircle";
import TicketLabel from "../shared/TicketLabel";
import React from "react";

export default function Ticket(props){
    let borderRadius;
    if (props.firstInRow && props.lastInRow){
        borderRadius = "0 0 10px 10px";
    }else if(props.firstInRow){
        borderRadius = "0 0 0 10px";
    }else if(props.lastInRow){
        borderRadius = "0 0 10px 0";
    }else{
        borderRadius = "0 0 0 0";
    }
    return(
        <DecorativeTicket
            borderRadius={borderRadius}
        >
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