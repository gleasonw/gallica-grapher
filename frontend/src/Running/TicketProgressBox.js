import TicketLabel from "../shared/TicketLabel";
import ProgressBar from "react-bootstrap/ProgressBar";
import React from "react";

export function TicketProgressBox(props) {
    const secondsToCompletion = props.progressStats.estimateSecondsToCompletion
    const minutesToCompletion = Math.floor(secondsToCompletion / 60)
    const hoursToCompletion = Math.floor(minutesToCompletion / 60)
    const remainingSeconds = Math.floor(secondsToCompletion % 60)
    const remainingMinutes = minutesToCompletion % 60
    const timeEstimate = hoursToCompletion + "h " + remainingMinutes + "m " + remainingSeconds + "s"
    return (
        <div className='ticketProgressBox'>
            <TicketLabel
                terms={props.terms}
                papers={props.papers}
                dateRange={props.dateRange}
            />
            {props.progressStats &&
            <div className='progressStats'>
                <ProgressBar
                    animated
                    now={props.progressStats.progress}
                />
                <div className='progressStatsText'>
                    {props.progressStats.numResultsRetrieved} of {props.progressStats.numResultsDiscovered} results
                    retrieved
                </div>
                <div className='progressStatsText'>
                    {props.progressStats.randomPaper}
                </div>
                <div className='progressStatsText'>
                    {timeEstimate} approximate time to completion
                </div>
            </div>
            }
        </div>
    )
}