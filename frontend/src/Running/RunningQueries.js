import React, {useState} from "react";
import {TicketProgressBox} from "./TicketProgressBox";
import useInterval from "../shared/useInterval";
import ImportantButtonWrap from "../shared/ImportantButtonWrap";
import ClassicUIBox from "../shared/ClassicUIBox";


//TODO: improve grouping change communication, perhaps on the backend. If the search is too fast, the front end won't have time to update the grouping before the search is complete.
function RunningQueriesUI(props) {
    const initialProgressStats = {}
    Object.keys(props.tickets).map((ticketId) => (
        initialProgressStats[ticketId] = {
            'numResultsDiscovered': 0,
            'numResultsRetrieved': 0,
            'progressPercent': 0,
            'estimateSecondsToCompletion': 0,
            'randomPaper': null,
            'randomText': null,
            'active': 0
        }
    ))
    const [cancelMessage, setCancelMessage] = useState('Cancel');
    const [progressStats, setProgressStats] = useState({});
    const [timeBeforeResponse, setTimeBeforeResponse] = useState(0);
    const refreshInterval = 1000;
    const timeBeforeWarning = 30000;
    const responseReceived = Object.keys(progressStats).some((ticketID) => (
        progressStats[ticketID].progressPercent > 0
    ))

    useInterval(async () => {
        const requestStateCallbacks = {
            "RUNNING": () => setProgressStats(progressJSON.progress ? progressJSON.progress : progressStats),
            "TOO_MANY_RECORDS": () => props.onTooManyRecords(progressJSON.numRecords),
            "NO_RECORDS": props.onNoRecords,
            "COMPLETED": () => {
                props.onFinish(progressJSON)
            },
            "PENDING": () => null,
            "ERROR": props.onBackendError,
        }
        const response = await fetch(`${process.env.REACT_APP_API_URL}/poll/progress/` + props.requestID);
        if (response.status === 500) {
            props.onBackendError();
        }
        const progressJSON = await response.json();
        const state = progressJSON.state
        if (requestStateCallbacks.hasOwnProperty(state)) {
            console.log(state);
            console.log(progressJSON);
            requestStateCallbacks[state]()
        } else {
            console.log("Unknown state: " + state)
        }
        if (!responseReceived) {
            setTimeBeforeResponse(timeBeforeResponse + refreshInterval)
        }
    }, refreshInterval);

    function handleCancelRequest() {
        setCancelMessage('Cancelling...');
        fetch(`/api/revokeTask/${props.requestID}`).then(
            props.onCancelRequest
        )
    }

    return (
        <div className='queryProgressUI'>
            {timeBeforeResponse > timeBeforeWarning && !responseReceived && <ClassicUIBox>
                <h3>It's taking a while to get a response from the archive.</h3>
                Sometimes it's a bit slow. You could try again later, or if you just want to flip through some old
                periodicals, try an example: they're pre-loaded.
            </ClassicUIBox>
            }
            {Object.keys(props.tickets).map((key, index) => (
                <TicketProgressBox
                    ticket={props.tickets[key]}
                    key={key}
                    index={index}
                    total={Object.keys(props.tickets).length}
                    progressStats={progressStats[key] || initialProgressStats[key]}
                    onBackendGroupingChange={() => props.onBackendGroupingChange(key)}
                />
            ))}
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
