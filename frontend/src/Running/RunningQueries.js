import React, {useEffect, useState} from "react";
import {TicketProgressBox} from "./TicketProgressBox";
import ClassicUIBox from "../shared/ClassicUIBox";


function RunningQueriesUI(props) {
    const [progressStats, setProgressStats] = useState(null)
    const [activeTicket, setActiveTicket] = useState(0)
    console.log(activeTicket)

    useEffect(() => {
        async function updateProgress() {
            const currentTicketProgress = await fetch("/api/progress/" + props.requestID);
            currentTicketProgress.json().then(data => {
                const state = data["state"]
                if(state === "PENDING"){
                    setTimeout(updateProgress, 1000)
                }else if (state === "PROGRESS") {
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

    function handleIncrementActiveTicket(){
        setActiveTicket(activeTicket + 1)
    }

    if(progressStats === null){
        return(
            <div className='queryProgressUI'>
                <ClassicUIBox>Your request has been received. A worker process will begin fetching records shortly...</ClassicUIBox>
            </div>
        )
    }else{
        return (
            <div className='queryProgressUI'>
                {Object.keys(props.tickets).map((key, index) => (
                    <TicketProgressBox
                        terms={props.tickets[key]['terms']}
                        papers={props.tickets[key]['papersAndCodes']}
                        dateRange={props.tickets[key]['dateRange']}
                        key={key}
                        active={index === activeTicket}
                        progressStats={progressStats[key]}
                        onFinish={handleIncrementActiveTicket}
                    />
                ))}
            </div>
        )
    }
}

export default RunningQueriesUI;