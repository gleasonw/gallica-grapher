import TicketLabel from "./TicketLabel";
import Chart from "./Chart";
import TicketPapers from "./TicketPapers";
import React from "react";

function SoloTickets(props) {
    return (
        <div className='ticketResultsContainer'>
            {Object.keys(props.tickets).map(key => (
                <SoloTicketResult
                    terms={props.tickets[key]["terms"]}
                    papers={props.tickets[key]["papersAndCodes"]}
                    dateRange={props.tickets[key]["dateRange"]}
                    key={key}
                    requestID={key}
                    settings={props.settings[key]}

                />
            ))}
        </div>
    )
}

function SoloTicketResult(props) {
    return (
        <div className='ticketResults'>
            <TicketLabel
                terms={props.terms}
                papers={props.papers}
                dateRange={props.dateRange}
            />
            <Chart options={props.options}/>

            <TicketPapers onClick={props.onClick}/>
        </div>
    )
}

export default SoloTickets;