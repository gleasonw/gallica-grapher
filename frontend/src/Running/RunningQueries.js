import React from "react";
import {TicketProgressBox} from "./TicketProgressBox";
import useInterval from "../shared/useInterval";
import ImportantButtonWrap from "../shared/ImportantButtonWrap";
import ClassicUIBox from "../shared/ClassicUIBox";


function RunningQueriesUI(props) {
    const [cancelMessage, setCancelMessage] = React.useState('Cancel');
    const [progressStats, setProgressStats] = React.useState({
        'init': {progress: 0}
    })
    const [displayState, setDisplayState] = React.useState('running');
    const [timeBeforeResponse, setTimeBeforeResponse] = React.useState(0);
    const refreshInterval = 1000;
    const timeBeforeWarning = 30000;
    const responseReceived = Object.keys(progressStats).some((ticketID) => (
        progressStats[ticketID].progress > 0
    ))
    useInterval(async () => {
        const requestStateCallbacks = {
            "PROGRESS": () => setProgressStats(
                progressJSON['progress'] ?
                    progressJSON['progress']
                    :
                    {}
            ),
            "TOO_MANY_RECORDS": () => props.onTooManyRecords(progressJSON['getNumRecords']),
            "NO_RECORDS": props.onNoRecords,
            "COMPLETED": props.onFinish,
            "PENDING": () => null,
            "ADDING_MISSING_PAPERS": () => setDisplayState('addingMissingPapers'),
            "ADDING_RESULTS": () => setDisplayState('addingResults'),
            "REMOVING_DUPLICATES": () => setDisplayState('removingDuplicates'),
            "ERROR": props.onBackendError,
        }
        const response = await fetch("/poll/progress/" + props.progressID);
        if (response.status === 500) {
            props.onBackendError();
        }
        const progressJSON = await response.json();
        const state = progressJSON["state"]
        if (requestStateCallbacks.hasOwnProperty(state)) {
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
        fetch(`/api/revokeTask/${props.progressID}/${props.requestID}`).then(
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
                    terms={props.tickets[key]['terms']}
                    papers={props.tickets[key]['papersAndCodes']}
                    dateRange={props.tickets[key]['dateRange']}
                    linkTerm={props.tickets[key]['linkTerm']}
                    linkDistance={props.tickets[key]['linkDistance']}
                    state={displayState}
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
