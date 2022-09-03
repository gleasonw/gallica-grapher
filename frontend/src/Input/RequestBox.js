import TicketLabel from "../shared/TicketLabel";
import React from "react";
import DecorativeTicket from "../shared/DecorativeTicket";

export function RequestBox(props) {
    return (
        <div className={'requestBoxContainer'}>
            <div className='requestBox'>
                <RequestTicketBox
                    tickets={props.tickets}
                    onTicketClick={props.onTicketClick}
                />
            </div>
        </div>
    );

}

function RequestTicketBox(props) {
    if (props.tickets && props.tickets.length > 0) {
        return (
            <div className="ticketBubbleContainer">
                {props.tickets.map((ticket, index) => (
                    <DecorativeTicket key={index}>
                        <RequestTicket
                            ticket={ticket}
                            onClick={() => props.onTicketClick(index)}
                        />
                    </DecorativeTicket>
                ))}
            </div>
        )
    } else {
        return (
            <div className="ticketBubbleContainer">
                <div id='placeHolderTicket'/>
            </div>
        )
    }
}

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