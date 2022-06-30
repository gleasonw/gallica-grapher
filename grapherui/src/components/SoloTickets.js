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
    const settings = useContext(
        GraphSettingsContext)[props.ticketID];
    const query =
        "/graphData?keys=" + props.ticketID +
        "&continuous=" + settings.continuous +
        "&dateRange=" + props.dateRange +
        "&timeBin=" + settings.timeBin +
        "&averageWindow=" + settings.averageWindow;

    const graphData = useData(query);
    const options = generateOptions(
        settings.timeBin,
        graphData)

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