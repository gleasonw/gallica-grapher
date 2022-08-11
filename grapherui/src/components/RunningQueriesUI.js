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
    const initProgressStats = {}

    Object.keys(props.tickets).map(key => (
        initProgressStats[key] = {
            progress: 0,
            numResultsDiscovered: 0,
            numResultsRetrieved: 0,
            randomPaper: ''
        }
    ))

    const [progressStats, setProgressStats] = useState(initProgressStats)

    useEffect(() => {
        async function updateProgress() {
            const currentTicketProgress = await fetch("progress/" + props.requestid);
            currentTicketProgress.json().then(data => {
                const progress = data["progress"]
                setProgressStats(progress ? progress : initProgressStats)
                if (data["state"] === "SUCCESS") {
                    props.onFinish()
                }
            });
        }
        setTimeout(updateProgress, 1000)
    }, [props, progressStats, initProgressStats]);
    return(
        <div className='queryProgressUI'>
            {Object.keys(props.tickets).map(key => (
                <TicketProgressBox
                    terms={props.tickets[key]['terms']}
                    papers={props.tickets[key]['papersAndCodes']}
                    dateRange={props.tickets[key]['dateRange']}
                    key={key}
                    progressStats={progressStats[key]}
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
            {props.progressStats &&
                <div className='progressStats'>
                    <ProgressBar
                        animated
                        now={props.progressStats.progress}
                    />
                    <div className='progressStatsText'>
                        {props.progressStats.numResultsRetrieved} of {props.progressStats.numResultsDiscovered} results retrieved
                    </div>
                    <div className='progressStatsText'>
                        {props.progressStats.randomPaper}
                    </div>
                </div>
            }
        </div>
    )
}

export default RunningQueriesUI;