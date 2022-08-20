import generateOptions from "./generateOptions";
import React, {useContext, useState} from "react";
import {GraphSettingsContext} from "./GraphSettingsContext";
import TicketStats from "./TicketStats";
import useData from "./useData";

function SoloTickets(props) {
    return (
        <div className='ticketResultsContainer'>
            {Object.keys(props.tickets).map(key => (
                <SoloTicketResult
                    ticket={props.tickets[key]}
                    key={key}
                    ticketID={key}
                />
            ))}
        </div>
    )
}

function SoloTicketResult(props) {
    return (
        <TicketStats
            ticket={props.ticket}
            ticketID={props.ticketID}
            grouped={false}
        />
    )
}

export default SoloTickets;