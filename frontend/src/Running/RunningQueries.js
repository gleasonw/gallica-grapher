import React from "react";
import {TicketProgressBox} from "./TicketProgressBox";
import useInterval from "../shared/useInterval";
import ClassicUIBox from "../shared/ClassicUIBox";
import {CircularProgress} from "@mui/material";
import ImportantButtonWrap from "../shared/ImportantButtonWrap";


function RunningQueriesUI(props) {
    const [cancelMessage, setCancelMessage] = React.useState('Cancel');
    const [progressStats, setProgressStats] = React.useState({
        'init': {progress: 0}
    })
    useInterval(async () => {
        const requestStateCallbacks = {
            "PROGRESS": () => setProgressStats(
                progressJSON['progress'] ?
                    progressJSON['progress']
                    :
                    {}
            ),
            "TOO_MANY_RECORDS": () => props.onTooManyRecords(progressJSON['numRecords']),
            "SUCCESS": props.onFinish,
            "PENDING": () => null,
        }
        const progress = await fetch("/poll/progress/" + props.progressID);
        const progressJSON = await progress.json();
        const state = progressJSON["state"]
        if(requestStateCallbacks.hasOwnProperty(state)){
            requestStateCallbacks[state]()
        }else{
            console.log("Unknown state: " + state)
        }
    }, 1000);

    const allDone = Object.keys(progressStats).every(
        key => progressStats[key].progress === 100
    );

    function handleCancelRequest(){
        setCancelMessage('Cancelling...');
        fetch("/api/revokeTask/" + props.requestID).then(
            props.onCancelRequest
        )
    }

    return (
        <div className='queryProgressUI'>
            {
                allDone ?
                    <ClassicUIBox>
                        Graphing results...
                        <CircularProgress/>
                    </ClassicUIBox>
                :
                    Object.keys(props.tickets).map((key, index) => (
                        <TicketProgressBox
                            terms={props.tickets[key]['terms']}
                            papers={props.tickets[key]['papersAndCodes']}
                            dateRange={props.tickets[key]['dateRange']}
                            key={key}
                            position={`${index + 1} of ${Object.keys(props.tickets).length}`}
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
                    ))
            }
            <ImportantButtonWrap
                background={'#d44e43'}
                color={'#ffffff'}
                hover={'none'}
                onClick={handleCancelRequest}
                children={cancelMessage}
            />
        </div>
    )
}

export default RunningQueriesUI;
