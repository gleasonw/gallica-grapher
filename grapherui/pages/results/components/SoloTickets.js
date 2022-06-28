import generateOptions from "./generateOptions";
import React, {useContext, useEffect} from "react";
import useSWR from "swr";
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
    const seriesQuery = "/graphData?keys=" + props.ticketID +
        "&averageWindow=" + settings.averageWindow +
        "&timeBin=" + settings.timeBin +
        "&continuous=" + settings.continuous

    const {series, error} = useSWR(seriesQuery, fetch);
    if(error) return "Error";
    if(!series) return "Loading...";

    const options = generateOptions(
        ticketSettings.timeBin,
        series)
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