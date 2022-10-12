import TicketLabel from "../shared/TicketLabel";
import ProgressBar from "react-bootstrap/ProgressBar";
import React from "react";
import styled from "styled-components";
import ClassicUIBox from "../shared/ClassicUIBox";
import {CircularProgress} from "@mui/material";

export function TicketProgressBox(props) {
    const secondsToCompletion = props.progressStats.estimateSecondsToCompletion
    const minutesToCompletion = Math.floor(secondsToCompletion / 60)
    const hoursToCompletion = Math.floor(minutesToCompletion / 60)
    const remainingSeconds = Math.floor(secondsToCompletion % 60)
    const remainingMinutes = minutesToCompletion % 60
    const timeEstimate = hoursToCompletion + "h " + remainingMinutes + "m " + remainingSeconds + "s"
    const active = props.progressStats.active
    const progress = props.progressStats.progressPercent
    const resultsRetrieved = props.progressStats.numResultsRetrieved
    const estimateTotal = props.progressStats.numResultsDiscovered
    console.log(props.progressStats)

    const displayStates = {
        'addingMissingPapers':
            <div>
                <h3>Fetching missing periodical data...</h3>
                <CircularProgress/>
            </div>,
        'addingResults':
            <div>
                <h3>Loading response data into the database...</h3>
                <CircularProgress/>
            </div>,
        'removingDuplicates':
            <div>
                <h3>Removing duplicate results (Gallica sometimes surfaces the same periodical from different
                    websites)...</h3>
                <CircularProgress/>
            </div>
    }

    return (
        <ClassicUIBox display={(active || progress === 100 || props.index === 0) ? 'flex' : 'none'}>
            <span>{props.index + 1} of {props.total}</span>
            <TicketLabel
                terms={props.ticket.terms}
                papers={props.ticket.papersAndCodes}
                dateRange={props.ticket.dateRange}
                linkTerm={props.ticket.linkTerm}
                linkDistance={props.ticket.linkDistance}
            />
            <StyledProgressStats>
                {
                    (progress === 0 && active) || (progress === 0 && props.index === 0) ?
                        <span>
                        Waiting for a response from the archive...
                        <CircularProgress/>
                    </span>
                        :
                        null
                }
                {
                    progress === 100 &&
                    <div>{resultsRetrieved.toLocaleString()} results retrieved after eliminating duplicates.</div>
                }
                <ProgressBar
                    animated
                    now={progress}/>
                {
                    (progress > 0) && (progress < 100) &&
                    <StyledProgressStats>
                        <div className='progressStatsText'>
                            <div>{resultsRetrieved.toLocaleString()} of {estimateTotal.toLocaleString()} records fetched
                                from Paris
                            </div>
                        </div>
                        <div className='progressStatsText'>
                            {props.progressStats.randomPaper}
                        </div>
                        <div className='progressStatsText'>
                            {timeEstimate} approximate time to completion
                        </div>
                    </StyledProgressStats>
                }
                {progress === 100 && !!active && displayStates[props.state]}
            </StyledProgressStats>
        </ClassicUIBox>
    )
}

const StyledProgressStats = styled.div`
    display: flex;
    flex-direction: column;
    gap: 30px;
    margin-top: 20px;
    `;