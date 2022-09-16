import React, {useEffect, useState} from "react";
import {TicketProgressBox} from "./TicketProgressBox";

export function TicketProgressContainer(props) {
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
                const state = data["state"]
                if(state === "PENDING"){
                    console.log("PENDING")
                    setTimeout(updateProgress, 1000)
                }
                if (state === "PROGRESS") {
                    const progress = data["progress"]
                    setProgressStats(progress)
                } else if (state === "SUCCESS") {
                    props.onFinish()
                } else if (state === "TOO_MANY_RECORDS") {
                    props.onTooManyRecords(data["numRecords"])
                } else {
                    console.log("Unknown state: " + data["state"])
                }
            });
        }
        setTimeout(updateProgress, 1000)
    }, [props, progressStats]);
    return (
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