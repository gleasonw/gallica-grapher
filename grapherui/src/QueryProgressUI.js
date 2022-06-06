import React,{useState, useEffect} from 'react';
import ProgressBar from 'react-bootstrap/ProgressBar';
import TicketLabel from "./TicketLabel";
import axios from "axios";


function QueryProgressUI(props) {
    const [ticketProgressPercents, setProgressPercents] = useState({});
    const [finished, setFinished] = useState(false);
    useEffect(() => {
        axios.post('/init', {
            tickets: props.tickets
        })
        .then(result => {
            let progressPercents = {}
            Object.keys(props.tickets).map(key => (
                progressPercents[key] = 0
            ))
            setProgressPercents(progressPercents)
            updateProgress(result.data["taskid"])
            })

        function updateProgress(taskid) {
            let progress = 0;
            let currentID = '';
            let state = '';
            fetch("progress/" + taskid)
                .then(res => res.json())
                .then(
                    (result) => {
                        progress = result["progress"]
                        currentID = result["currentID"]
                        state = result["state"]
                    }
                )
            let updatedProgressPercents = structuredClone(ticketProgressPercents)
            updatedProgressPercents[currentID] = progress
            setProgressPercents(updatedProgressPercents)
            if (state === "SUCCESS"){
                setFinished(true);
            }else{
                setTimeout(updateProgress, 1000, taskid);
            }
        }
    }, [props.tickets, ticketProgressPercents])
    return(
        <div className='queryProgressUI'>
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

export default QueryProgressUI;