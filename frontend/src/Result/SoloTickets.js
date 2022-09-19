import React, {useContext} from "react";
import TicketLabel from "../shared/TicketLabel";
import TicketPaperOccurrenceStats from "./TicketPaperOccurrenceStats";
import DownloadCSVButton from "./DownloadCSVButton";
import ClassicUIBox from "../shared/ClassicUIBox";
import RecordsViewer from "./RecordsViewer";
import {GraphSettingsContext} from "./GraphSettingsContext";

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
    const settings = useContext(GraphSettingsContext);
    const ticketSettings = settings[props.ticketID];
    const timeBin = ticketSettings.timeBin;
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
                timeBin={timeBin}
            />
            <TicketPaperOccurrenceStats
                ticketID={props.ticketID}
                dateRange={props.ticket.dateRange}
                grouped={false}
                requestID={props.requestID}
            />
        </ClassicUIBox>
    )
}

export default SoloTickets;