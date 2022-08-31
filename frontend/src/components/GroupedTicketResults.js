import React, {useContext} from "react";
import {GraphSettingsContext} from "./GraphSettingsContext";
import TicketLabel from "./TicketLabel";
import Chart from "./Chart";
import TicketPaperOccurrenceStats from "./TicketPaperOccurrenceStats";
import Button from "@mui/material/Button";

export function GroupedTicketResults(props) {
    return (
        <div className='groupedResultsUI'>
            <Chart
                tickets={props.tickets}
                settingsID='group'
            />
            <GroupedStatBar
                tickets={props.tickets}/>
        </div>

    )
}

function GroupedStatBar(props) {
    const settings = useContext(GraphSettingsContext);

    function downloadGroupCSV() {
        console.log(Object.keys(props.tickets))
        const ticketIDs = Object.keys(props.tickets);
        const query = "/api/getcsv?tickets=" + ticketIDs.join(",");
        window.open(query, "_blank");
    }

    return (
        <div className='groupedStatBar'>
            <Button
                variant="contained"
                className={'downloadGroupCSVbutton'}
                onClick={() => downloadGroupCSV(props.tickets)}
            >
                Download Grouped CSV
            </Button>
            {Object.keys(props.tickets).map(key => (
                <div
                    className='groupedStatBarEntry'
                    key={key}
                >
                    <svg width = "20" height="20">
                        <circle cx="10" cy="10" r="10" fill={settings[key].color}/>
                    </svg>
                    <TicketLabel
                        terms={props.tickets[key].terms}
                        papers={props.tickets[key].papersAndCodes}
                        dateRange={props.tickets[key].dateRange}
                    />
                    <TicketPaperOccurrenceStats
                        ticketID={key}
                        dateRange={props.tickets[key].dateRange}
                        grouped={true}
                    />
                </div>
            ))}
        </div>
    );
}

export default GroupedTicketResults;