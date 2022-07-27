import React, {useContext} from "react";
import {GraphSettingsContext} from "./GraphSettingsContext";
import TicketLabel from "./TicketLabel";
import Chart from "./Chart";
import generateOptions from "./generateOptions"
import TicketStats from "./TicketStats";
import useData from "./useData";

export function GroupedTicketResults(props) {
    return (
        <div className='groupedResultsUI'>
            <GroupedTicketLabelBar tickets={props.tickets}/>
            <GroupedChart tickets={props.tickets}/>
            <GroupedStatBar tickets={props.tickets}/>
        </div>

    )
}
//TODO: Sync label color with line color
function GroupedTicketLabelBar(props) {
    const highChartsSeriesColors = [
        '#0066ff', '#ff0000', '#ff9900', '#00ff00',
        '#0000ff', '#ff00ff', '#00ffff', '#ffff00',
        '#000000'];
    //TODO: add color to each ticket
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
function GroupedChart(props) {
    const settings = useContext(GraphSettingsContext).group;
    const timeBin = settings.timeBin;
    const dateRange = getWidestDateRange(props.tickets);
    const query =
        "/graphData?keys=" + Object.keys(props.tickets) +
        "&continuous=" + settings.continuous +
        "&dateRange=" + dateRange +
        "&timeBin=" + settings.timeBin +
        "&averageWindow=" + settings.averageWindow;
    const series = useData(query);

    return (
        <div>
            <Chart
                options={generateOptions(timeBin, series)}
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

function getWidestDateRange(tickets) {
    let widestDateRange = 0;
    let widestTicket = null;
    Object.keys(tickets).forEach(key => {
        const lowYear = tickets[key].dateRange[0];
        const highYear = tickets[key].dateRange[1];
        const thisWidth = highYear - lowYear;
        if (thisWidth > widestDateRange) {
            widestDateRange = thisWidth;
            widestTicket = key;
        }
    }
    )
    return tickets[widestTicket].dateRange;
}

export default GroupedTicketResults;