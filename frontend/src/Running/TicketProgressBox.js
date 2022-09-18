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
    const progress = props.progressStats.progress
    return (
        <ClassicUIBox>
            <TicketLabel
                terms={props.terms}
                papers={props.papers}
                dateRange={props.dateRange}
            />
            <StyledProgressStats>
                <ProgressBar
                    animated
                    now={props.progressStats.progress}
                />
                {
                    progress === 0 &&
                    <CircularProgress/>
                }
                {
                    progress === 100 &&
                    <div>{props.progressStats.numResultsRetrieved.toLocaleString()} results retrieved after eliminating duplicates.</div>
                }
                {
                    (props.progressStats.progress > 0) && (props.progressStats.progress < 100)  &&
                    <StyledProgressStats>
                        <div className='progressStatsText'>
                            <div>{props.progressStats.numResultsRetrieved.toLocaleString()} of {props.progressStats.numResultsDiscovered.toLocaleString()} records fetched from Paris</div>
                        </div>
                        <div className='progressStatsText'>
                            {props.progressStats.randomPaper}
                        </div>
                        <div className='progressStatsText'>
                        {timeEstimate} approximate time to completion
                        </div>
                    </StyledProgressStats>
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