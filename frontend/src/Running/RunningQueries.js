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
    const [displayState, setDisplayState] = React.useState('running');

    const stateDisplays = {
        'running':
            Object.keys(props.tickets).map((key, index) => (
                <TicketProgressBox
                    terms={props.tickets[key]['terms']}
                    papers={props.tickets[key]['papersAndCodes']}
                    dateRange={props.tickets[key]['dateRange']}
                    linkTerm={props.tickets[key]['linkTerm']}
                    linkDistance={props.tickets[key]['linkDistance']}
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
            )),
        'addingMissingPapers':
            <ClassicUIBox>
                <h2>Fetching missing periodical data...</h2>
                <CircularProgress/>
            </ClassicUIBox>,
        'addingResults':
            <ClassicUIBox>
                <h2>Loading response data into my database...</h2>
                <CircularProgress/>
            </ClassicUIBox>,
        'removingDuplicates':
            <ClassicUIBox>
                <h2>Removing duplicate results (Gallica sometimes surfaces the same periodical from different websites)...</h2>
                <CircularProgress/>
            </ClassicUIBox>,
    }
    useInterval(async () => {
        const requestStateCallbacks = {
            "PROGRESS": () => setProgressStats(
                progressJSON['progress'] ?
                    progressJSON['progress']
                    :
                    {}
            ),
            "TOO_MANY_RECORDS": () => props.onTooManyRecords(progressJSON['numRecords']),
            "NO_RECORDS": props.onNoRecords,
            "SUCCESS": props.onFinish,
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
    }, 1000);

    function handleCancelRequest() {
        setCancelMessage('Cancelling...');
        fetch(`/api/revokeTask/${props.progressID}/${props.requestID}`).then(
            props.onCancelRequest
        )
    }

    return (
        <div className='queryProgressUI'>
            {stateDisplays[displayState]}
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
