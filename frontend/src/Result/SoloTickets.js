import React from "react";
import TicketLabel from "../shared/TicketLabel";
import TicketPaperOccurrenceStats from "./TicketPaperOccurrenceStats";
import ClassicUIBox from "../shared/ClassicUIBox";
import RecordsViewer from "./RecordsViewer";
import {v4 as uuidv4} from 'uuid';

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
//TODO: sync timebin display with state
function SoloTicketResult(props) {
    const uniqueIDToPreventCaching = uuidv4();
    return (
        <ClassicUIBox resize={'both'}>
            <TicketLabel
                terms={props.ticket.terms}
                papers={props.ticket.papersAndCodes}
                dateRange={props.ticket.dateRange}
            />
            <RecordsViewer
                tickets={{[props.ticketID]: props.ticket}}
                requestID={props.requestID}
                settingsID={props.ticketID}
            />
            <TicketPaperOccurrenceStats
                ticketID={props.ticketID}
                dateRange={props.ticket.dateRange}
                grouped={false}
                requestID={props.requestID}
                uuid={uniqueIDToPreventCaching}
            />
        </ClassicUIBox>
    )
}

export default SoloTickets;