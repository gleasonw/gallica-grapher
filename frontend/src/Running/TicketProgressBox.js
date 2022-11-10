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
    const resultsRetrieved = props.progressStats.numResultsRetrieved
    const estimateTotal = props.progressStats.numResultsDiscovered
    const ticketSearchState = props.progressStats.state
    const progress = ticketSearchState === 'COMPLETED' ? 100 : props.progressStats.progressPercent
    const backendGrouping = props.progressStats.grouping;
    backendGrouping && backendGrouping !== props.ticket.grouping && props.onBackendGroupingChange()

    return (
        <ClassicUIBox display={(
            ticketSearchState === 'RUNNING' ||
            progress === 100 ||
            props.index === 0) ? 'flex' : 'none'}
        >
            <span>{props.index + 1} of {props.total}</span>
            <TicketLabel
                terms={props.ticket.terms}
                papers={props.ticket.papersAndCodes}
                startDate={props.ticket.startDate}
                endDate={props.ticket.endDate}
                linkTerm={props.ticket.linkTerm}
                linkDistance={props.ticket.linkDistance}
            />
            <StyledProgressStats>
                {
                    (ticketSearchState === 'RUNNING' || props.index === 0) && estimateTotal === 0 &&
                    <span>
                        Waiting for a response from the archive...
                        <CircularProgress/>
                    </span>
                }
                <ProgressBar
                    animated
                    now={progress}
                />
                {
                    ticketSearchState === 'COMPLETE' &&
                    <div>{resultsRetrieved.toLocaleString()} results retrieved after eliminating duplicates.</div>
                }
                {
                    ticketSearchState === 'RUNNING' &&
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
                {
                    ticketSearchState === "ADDING_MISSING_PAPERS" &&
                    <div>
                        <h3>Fetching missing periodical data...</h3>
                        <CircularProgress/>
                    </div>
                }
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