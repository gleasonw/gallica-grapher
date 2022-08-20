import React, {useContext} from "react";
import {GraphSettingsContext} from "./GraphSettingsContext";
import TicketLabel from "./TicketLabel";
import Chart from "./Chart";
import TicketStats from "./TicketStats";

export function GroupedTicketResults(props) {
    return (
        <div className='groupedResultsUI'>
            <GroupedTicketLabelBar tickets={props.tickets}/>
            <Chart
                tickets={props.tickets}
                settingsID='group'/>
            <GroupedStatBar tickets={props.tickets}/>
        </div>

    )
}
//TODO: Sync label color with line color
function GroupedTicketLabelBar(props) {
    const settings = useContext(GraphSettingsContext);
    return (
        <div className='groupedLabelBar'>
            {
                Object.keys(props.tickets).map(key => (
                    <div>
                        <svg width = "20" height="20">
                            <circle cx="10" cy="10" r="10" fill={settings[key].color}/>
                        </svg>
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