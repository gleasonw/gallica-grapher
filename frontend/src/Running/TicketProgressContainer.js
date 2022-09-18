import React, {useEffect, useState} from "react";
import {TicketProgressBox} from "./TicketProgressBox";
import ClassicUIBox from "../shared/ClassicUIBox";

export function TicketProgressContainer(props) {
    const [progressStats, setProgressStats] = useState(null)

    useEffect(() => {
        async function updateProgress() {
            const currentTicketProgress = await fetch("/api/progress/" + props.requestid);
            currentTicketProgress.json().then(data => {
                const state = data["state"]
                if(state === "PENDING"){
                    setTimeout(updateProgress, 1000)
                } if (state === "PROGRESS") {
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
    if(progressStats === null){
        return(
            <div className='queryProgressUI'>
                <ClassicUIBox>Your request has been received. A worker process will begin fetching records shortly...</ClassicUIBox>
            </div>
        )
    }else{
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
}