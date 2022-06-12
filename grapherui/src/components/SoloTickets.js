import generateOptions from "./generateOptions";
import React, {useContext} from "react";
import {GraphSettingsContext} from "./GraphSettingsContext";
import TicketStats from "./TicketStats";

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
    const settings = useContext(GraphSettingsContext);
    const ticketSettings = settings[props.ticketID];
    const options = generateOptions(
        ticketSettings.timeBin,
        ticketSettings.series)
    return (
        <TicketStats
            ticket={props.ticket}
            ticketID={props.ticketID}
            grouped={false}
            options={options}
        />
    )
}

export default SoloTickets;