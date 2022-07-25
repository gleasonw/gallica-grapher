import React from 'react';
import TicketLabel from "./TicketLabel";
import Chart from "./Chart";
import TicketPapers from "./TicketPapers";

export default function TicketStats(props){
    return(
        <div className={props.grouped ? 'ticketResults' : 'groupedStat'}>
            <TicketLabel
                terms={props.ticket.terms}
                papers={props.ticket.papersAndCodes}
                dateRange={props.ticket.dateRange}
            />
            {!props.grouped &&
                <Chart
                    options={props.options}
                    settingsID={props.ticketID}
                />
            }
            <TicketPapers
                ticketID={props.ticketID}
                dateRange={props.ticket.dateRange}
                grouped={props.grouped}
            />
        </div>
    )
}