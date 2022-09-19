import React from "react";
import TicketLabel from "../shared/TicketLabel";
import TicketPaperOccurrenceStats from "./TicketPaperOccurrenceStats";
import Chart from "./Chart";
import DownloadCSVButton from "./DownloadCSVButton";
import ClassicUIBox from "../shared/ClassicUIBox";
import DisplayRecordsTable from "./DisplayRecordsTable";

function SoloTickets(props) {
    return (
        <div className='ticketResultsContainer'>
            {Object.keys(props.tickets).map(key => (
                <SoloTicketResult
                    ticket={props.tickets[key]}
                    key={key}
                    ticketID={key}
                    requestID={props.requestID}
                />
            ))}
        </div>
    )
}

function SoloTicketResult(props) {
    return (
        <ClassicUIBox resize={'both'}>
            <TicketLabel
                terms={props.ticket.terms}
                papers={props.ticket.papersAndCodes}
                dateRange={props.ticket.dateRange}
            />
            <Chart
                tickets={{[props.ticketID]: props.ticket}}
                settingsID={props.ticketID}
            />
            <DisplayRecordsTable
                tickets={{[props.ticketID]: props.ticket}}
                requestID={props.requestID}
            />
            <TicketPaperOccurrenceStats
                ticketID={props.ticketID}
                dateRange={props.ticket.dateRange}
                grouped={false}
                requestID={props.requestID}
            />
            <DownloadCSVButton
                tickets={{[props.ticketID]: ''}}
                requestID={props.requestID}
            />
        </ClassicUIBox>
    )
}

export default SoloTickets;