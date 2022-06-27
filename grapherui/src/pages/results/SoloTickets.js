import generateOptions from "./generateOptions";
import fetchSeries from "./fetchSeries";
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
        let ignore = false;

        async function updateSeries(){
            try{
                const series = await fetchSeries(props.ticketID, ticketSettings);
                if(!ignore) {
                    setSeries(series);
                    setLoaded(true);
                }
            }catch(error){
                if(!ignore) {
                    setLoaded(true);
                    setError(error);
                }
            }
        }

        // noinspection JSIgnoredPromiseFromCall
        updateSeries();

        return () => {
            ignore = true;
        };

    }, [ticketSettings, props.ticketID])

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