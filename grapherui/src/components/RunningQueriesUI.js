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

    const [progressStats, setProgressStats] = useState(initPercents)

    useEffect(() => {
        async function updateProgress() {
            let progress = 0;
            let state = '';
            const currentTicketProgress = await fetch("progress/" + props.requestid);
            currentTicketProgress.json().then(data => {
                progress = data["progress"]
                setProgressStats(progress)
                state = data["state"]
                if (state === "SUCCESS") {
                    props.onFinish()
                }
            });
        }
        setTimeout(updateProgress, 1000)
    }, [props, progressStats]);

    return(
        <div className='queryProgressUI'>
            {Object.keys(props.tickets).map(key => (
                <TicketProgressBox
                    terms={props.tickets[key]['terms']}
                    papers={props.tickets[key]['papersAndCodes']}
                    dateRange={props.tickets[key]['dateRange']}
                    key={key}
                    progress={progressStats[key]}
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