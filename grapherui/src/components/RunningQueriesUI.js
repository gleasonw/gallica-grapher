import React,{useState, useEffect, useCallback} from 'react';
import ProgressBar from 'react-bootstrap/ProgressBar';
import TicketLabel from "./TicketLabel";
import axios from "axios";


function RunningQueriesUI(props) {
    const [requestID, setRequestID] = useState('');
    useEffect(() => {
        axios.post('/init', {
            tickets: props.tickets
        })
            .then(result => {
                setRequestID(result.data["taskid"])
            })
    }, [props.tickets]);
    return(
        <div>
            <TicketProgressContainer
                tickets={props.tickets}
                requestid={requestID}
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
                        props.setRunningQueries(false);
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
    console.log(props.progress)
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