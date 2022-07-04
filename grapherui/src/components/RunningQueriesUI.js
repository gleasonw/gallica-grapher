import React,{useState, useEffect, useLayoutEffect} from 'react';
import ProgressBar from 'react-bootstrap/ProgressBar';
import TicketLabel from "./TicketLabel";



function RunningQueriesUI(props) {
    return(
        <div>
            <TicketProgressContainer
                tickets={props.tickets}
                requestid={props.requestID}
                setRunningQueries={props.setRunningQueries}
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
//TODO: Exiting before final render
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
                        console.log('finisehd')
                        setTimeout(props.setRunningQueries, 1000, false);
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