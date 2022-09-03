import React,{useState, useEffect} from 'react';
import ProgressBar from 'react-bootstrap/ProgressBar';
import TicketLabel from "../shared/TicketLabel";



function RunningQueriesUI(props) {
    return(
        <div>
            <TicketProgressContainer
                tickets={props.tickets}
                requestid={props.requestID}
                onFinish={props.onFinish}
                onTooManyRecords={props.onTooManyRecords}
            />
        </div>
    )
}

function TicketProgressContainer(props){
    let initProgressStats = {}

    Object.keys(props.tickets).map(key => (
        initProgressStats[key] = {
            progress: 0,
            numResultsDiscovered: 0,
            numResultsRetrieved: 0,
            randomPaper: '',
            estimateSecondsToCompletion: 0
        }
    ))

    const [progressStats, setProgressStats] = useState(initProgressStats)

    useEffect(() => {
        async function updateProgress() {
            const currentTicketProgress = await fetch("/api/progress/" + props.requestid);
            currentTicketProgress.json().then(data => {
                if(data["state"] === "PROGRESS") {
                    const progress = data["progress"]
                    setProgressStats(progress)
                }else if (data["state"] === "SUCCESS") {
                    props.onFinish()
                }else if (data["state"] === "TOO_MANY_RECORDS") {
                    props.onTooManyRecords(data["numRecords"])
                }else{
                    console.log("Unknown state: " + data["state"])
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
                    progressStats={progressStats[key]}
                />
            ))}
        </div>
    )

}
function TicketProgressBox(props){
    const secondsToCompletion = props.progressStats.estimateSecondsToCompletion
    const minutesToCompletion = Math.floor(secondsToCompletion / 60)
    const hoursToCompletion = Math.floor(minutesToCompletion / 60)
    const remainingSeconds = Math.floor(secondsToCompletion % 60)
    const remainingMinutes = minutesToCompletion % 60
    const timeEstimate = hoursToCompletion + "h " + remainingMinutes + "m " + remainingSeconds + "s"
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
                    <div className='progressStatsText'>
                        {timeEstimate} approximate time to completion
                    </div>
                </div>
            }
        </div>
    )
}

export default RunningQueriesUI;