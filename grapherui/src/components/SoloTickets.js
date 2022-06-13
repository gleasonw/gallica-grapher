import generateOptions from "./generateOptions";
import updateSeries from "./updateSeries";
import React, {useContext, useEffect, useState} from "react";
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
    const [error, setError] = useState(null);
    const [loaded, setLoaded] = useState(false);
    const [series, setSeries] = useState({});

    useEffect(() => {
        if(!props.series){
            updateSeries(
                props.ticketID,
                ticketSettings
            ).then(
                (result) => {
                    setLoaded(true);
                    setSeries(result);
                },
                (error) => {
                    setLoaded(true);
                    setError(error);
                }
            )
        }else{
            setSeries(props.series)
        }
    }, [props.series, ticketSettings, props.ticketID])
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