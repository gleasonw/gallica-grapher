import React, {useEffect, useState, useContext} from "react";
import {GraphSettingsContext} from "./GraphSettingsContext";
import TicketLabel from "./TicketLabel";
import Chart from "./Chart";
import TicketPapers from "./TicketPapers";
import generateOptions from "./generateOptions"

export function GroupedTicketResults(props) {
    return (
        <div className='groupedResultsUI'>
            <GroupedTicketLabelBar tickets={props.tickets}/>
            <GroupedChart/>
            <GroupedStatBar tickets={props.tickets}/>
        </div>

    )
}
//TODO: Sync label color with line color
function GroupedTicketLabelBar(props) {
    return (
        <div className='groupedLabelBar'>
            {Object.keys(props.tickets).map(key => (
                <div className = 'groupedLabel'>
                    <TicketLabel
                        terms={props.tickets[key].terms}
                        papers={props.tickets[key].papersAndCodes}
                        dateRange={props.tickets[key].dateRange}
                        key={key}
                    />
                </div>
            ))}
        </div>
    );
}

function GroupedChart(props) {
    const settings = useContext(GraphSettingsContext);
    const groupSettings = settings.group;

    const timeBin = groupSettings.timeBin;
    const keyedSeries = groupSettings.series;
    const [options, setOptions] = useState({});

    useEffect(() => {
        let groupedSeries = [];
        groupedSeries.push(
            Object.keys(keyedSeries).map(key =>
            keyedSeries[key]
        ))
        setOptions(generateOptions(timeBin, groupedSeries))
    },[keyedSeries, timeBin])

    return (
        <div>
            <Chart
                options={options}
                settingsID='group'
            />
        </div>
    )
}

function GroupedStatBar(props) {
    const settings = useContext(GraphSettingsContext);
    return (
        <div className='groupedStatBar'>
            {Object.keys(props.tickets).map(key => (
                <GroupedTicketStat
                    ticket={props.tickets[key]}
                    settings={settings[key]}
                    ticketID={key}
                    key={key}
                />
            ))}
        </div>
    );
}

function GroupedTicketStat(props) {
    return (
        <div className='groupedStat'>
            <TicketLabel
                terms={props.ticket.terms}
                papers={props.ticket.papers}
                dateRange={props.ticket.dateRange}
            />
            <TicketPapers
                ticketID={props.ticketID}
                continuous={props.settings.continuous}
                dateRange={props.ticket.dateRange}
            />
        </div>
    )
}

export default GroupedTicketResults;