import React from "react";
import TicketLabel from "../shared/TicketLabel";
import TicketPaperOccurrenceStats from "./TicketPaperOccurrenceStats";
import Chart from "./Chart";
import DownloadCSVButton from "./DownloadCSVButton";

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
    return (
        <div className='ticketResults'>
            <TicketLabel
                terms={props.ticket.terms}
                papers={props.ticket.papersAndCodes}
                dateRange={props.ticket.dateRange}
            />
            <Chart
                tickets={{[props.ticketID]: props.ticket}}
                settingsID={props.ticketID}
            />
            <TicketPaperOccurrenceStats
                ticketID={props.ticketID}
                dateRange={props.ticket.dateRange}
                grouped={false}
            />
            <DownloadCSVButton tickets={{[props.ticketID]: ''}}/>
        </div>
    )
}

export default SoloTickets;