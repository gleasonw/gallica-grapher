import React from "react";
import TicketLabel from "../shared/TicketLabel";
import ClassicUIBox from "../shared/ClassicUIBox";
import RecordsViewer from "./RecordsViewer";
import styled from 'styled-components';

function SoloTickets(props) {
    return (
        <div className='ticketResultsContainer'>
            {Object.keys(props.tickets).map(key => (
                <SoloTicketResult
                    ticket={props.tickets[key]}
                    key={key}
                    ticketID={key}
                    requestID={props.requestID}
                    cacheID={props.cacheID}
                />
            ))}
        </div>
    )
}
//TODO: sync timebin display with state
function SoloTicketResult(props) {
    return (
        <StyledSoloTicket>
            <ClassicUIBox>
                <TicketLabel
                    terms={props.ticket.terms}
                    papers={props.ticket.papersAndCodes}
                    startDate={props.ticket.startDate}
                    endDate={props.ticket.endDate}
                    linkTerm={props.ticket.linkTerm}
                    linkDistance={props.ticket.linkDistance}
                    compact={false}
                    center
                />
            </ClassicUIBox>
            <RecordsViewer
                tickets={{[props.ticketID]: props.ticket}}
                requestID={props.requestID}
                settingsID={props.ticketID}
                cacheID={props.cacheID}
            />
        </StyledSoloTicket>
    )
}
const StyledSoloTicket = styled.div`
    display: flex;
    flex-direction: column;
`
export default SoloTickets;