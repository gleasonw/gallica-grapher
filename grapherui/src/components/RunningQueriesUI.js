import React,{useState, useEffect} from 'react';
import ProgressBar from 'react-bootstrap/ProgressBar';
import TicketLabel from "./TicketLabel";



function RunningQueriesUI(props) {
    return(
        <div>
            <TicketProgressContainer
                tickets={props.tickets}
                requestid={props.requestID}
                onFinish={props.onFinish}
            />
        </div>
    )
}

function TicketProgressContainer(props){
    const initPercents = {}

    Object.keys(props.tickets).map(key => (
        initPercents[key] = 0
    ))

    const [ticketProgressPercents, setTicketProgressPercents] = useState(initPercents)
    //TODO: this is broken, not updating progress for next ticket
    useEffect(() => {
        function updateProgress(){
            let progress = 0;
            let currentTicket = '';
            let state = '';
            fetch("progress/" + props.requestid)
                .then(res => res.json())
                .then(result => {
                    progress = result["progress"]
                    currentTicket = result["currentID"]
                    state = result["state"]
                    let updatedTickets = structuredClone(ticketProgressPercents)
                    updatedTickets[currentTicket] = progress
                    setTicketProgressPercents(updatedTickets)
                    if (state === "SUCCESS") {
                        setTimeout(props.onFinish, 1000)
                    }
                });
        }
        setTimeout(updateProgress, 1000)
    }, [props, ticketProgressPercents]);

    return(
        <div  className='queryProgressUI'>
            {Object.keys(props.tickets).map(key => (
                <TicketProgressBox
                    terms={props.tickets[key]['terms']}
                    papers={props.tickets[key]['papersAndCodes']}
                    dateRange={props.tickets[key]['dateRange']}
                    key={key}
                    progress={ticketProgressPercents[key]}
                />
            ))}
        </div>
    )

}
function TicketProgressBox(props){
    return(
        <div className='ticketProgressBox'>
            <TicketLabel
                terms={props.terms}
                papers={props.papers}
                dateRange={props.dateRange}
            />
            <ProgressBar
                animated
                now={props.progress}
            />
        </div>
    )
}

export default RunningQueriesUI;