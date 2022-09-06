import TicketLabel from "../shared/TicketLabel";
import React from "react";
import DecorativeTicket from "../shared/DecorativeTicket";
import styled from 'styled-components';

export function RequestBox(props, className) {
    return (
        <div className={className}>
            {props.tickets ?
                props.tickets.map((ticket, index) => (
                    <DecorativeTicket key={index}>
                        <RequestTicket
                            ticket={ticket}
                            onClick={() => props.onTicketClick(index)}
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

