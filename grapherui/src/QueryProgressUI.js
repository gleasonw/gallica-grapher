import React,{useState, useEffect} from 'react';
import ProgressBar from 'react-bootstrap/ProgressBar';
import TicketLabel from "./TicketLabel";
import axios from "axios";

function QueryProgressUI(props) {
    const [ticketProgressPercents, setProgressPercents] = useState([]);
    useEffect(() => {
        axios.post('/init', {
            tickets: props.tickets
        }).then(taskid => {
            updateProgress(taskid)
        })
        }
    )
    function updateProgress(){

    }
    return(
        <div className='queryProgressUI'>
            {props.tickets.map(ticket => (
                <TicketProgressBox
                    terms={ticket['terms']}
                    papers={ticket['papersAndCodes']}
                    dateRange={ticket['dateRange']}
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
                now={45}
            />
        </div>
    )
}

export default QueryProgressUI;