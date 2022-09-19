import React from "react";
import {TicketProgressBox} from "./TicketProgressBox";
import useInterval from "../shared/useInterval";


function RunningQueriesUI(props) {
    const [progressStats, setProgressStats] = React.useState({})
    useInterval(async () => {
        const requestStateCallbacks = {
            "PROGRESS": () => setProgressStats(
                progressJSON['progress'] ?
                    progressJSON['progress']
                    :
                    {}
            ),
            "TOO_MANY_RECORDS": props.onTooManyRecords,
            "SUCCESS": props.onFinish
        }
        const progress = await fetch("/api/progress/" + props.requestID);
        const progressJSON = await progress.json();
        const state = progressJSON["state"]
        if(requestStateCallbacks.hasOwnProperty(state)){
            requestStateCallbacks[state]()
        }else{
            console.log("Unknown state: " + state)
        }
    }, 1000);
    return (
        <div className='queryProgressUI'>
            {Object.keys(props.tickets).map((key, index) => (
                <TicketProgressBox
                    terms={props.tickets[key]['terms']}
                    papers={props.tickets[key]['papersAndCodes']}
                    dateRange={props.tickets[key]['dateRange']}
                    key={key}
                    progressStats={
                        progressStats.hasOwnProperty(key) ?
                            progressStats[key]
                            :
                            {
                                progress: 0,
                                numResultsDiscovered: 0,
                                numResultsRetrieved: 0,
                                randomPaper: '',
                                estimateSecondsToCompletion: 0,
                                active: index === 0 ? 1 : 0
                            }

                    }
                />
            ))}
        </div>
    )
}

export default RunningQueriesUI;