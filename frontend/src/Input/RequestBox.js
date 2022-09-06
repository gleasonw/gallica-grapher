import TicketLabel from "../shared/TicketLabel";
import React from "react";
import DecorativeTicket from "../shared/DecorativeTicket";
import styled from 'styled-components';

export function RequestBox(props, className) {
    return (
        <div className={className}>
            {props.tickets ?
                Object.keys(props.tickets).map(ticketID => (
                    <DecorativeTicket key={ticketID}>
                        <RequestTicket
                            ticket={props.tickets[ticketID]}
                            onClick={() => props.onTicketClick(ticketID)}
                        />
                    </DecorativeTicket>
                    ))
                : null
            }

        </div>
    )
}

export const StyledRequestBox = styled(RequestBox)`
    display: ${props => props.display};
    
`;

function RequestTicket(props) {
    const terms = props.ticket['terms']
    const papers = props.ticket['papersAndCodes']
    const dateRange = props.ticket['dateRange']
    return (
        <button
            type="button"
            onClick={props.onClick}
        >
            <div className="ticket">
                <TicketLabel
                    terms={terms}
                    papers={papers}
                    dateRange={dateRange}
                />
            </div>
        </button>
    );
}

