import TicketLabel from "./TicketLabel";
import Chart from "./Chart";
import TicketPapers from "./TicketPapers";
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
            grouped={false}
            options={options}
            ticketID={props.ticketID}

        />
    )
}

export default SoloTickets;