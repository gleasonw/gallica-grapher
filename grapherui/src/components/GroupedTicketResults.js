import React, {useEffect, useState, useContext} from "react";
import {GraphSettingsContext} from "./GraphSettingsContext";
import TicketLabel from "./TicketLabel";
import Chart from "./Chart";
import generateOptions from "./generateOptions"
import TicketStats from "./TicketStats";

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
                <TicketLabel
                    terms={props.tickets[key].terms}
                    papers={props.tickets[key].papersAndCodes}
                    dateRange={props.tickets[key].dateRange}
                    key={key}
                />
            ))}
        </div>
    );
}
//TODO: ensure the object series --> array series works
function GroupedChart() {
    const settings = useContext(GraphSettingsContext);
    const groupSettings = settings.group;

    const timeBin = groupSettings.timeBin;
    const keyedSeries = groupSettings.series;
    const [options, setOptions] = useState({});
    useEffect(() => {
        let groupedSeries =
            Object.keys(keyedSeries).map(key =>
            keyedSeries[key])
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
    return (
        <div className='groupedStatBar'>
            {Object.keys(props.tickets).map(key => (
                <TicketStats
                    key={key}
                    ticket={props.tickets[key]}
                    ticketID={key}
                    grouped={true}
                />
            ))}
        </div>
    );
}

export default GroupedTicketResults;