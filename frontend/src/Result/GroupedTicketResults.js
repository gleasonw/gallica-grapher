import React from "react";
import RecordsViewer from "./RecordsViewer";
import TicketLabelRow from "../Input/TicketLabelRow";

export function GroupedTicketResults(props) {
    return (
        <div>
            <TicketLabelRow
                tickets={props.tickets}
                onTicketClick={(e) => console.log(e)}
                isMutable={false}
            />
            <RecordsViewer
                tickets={props.tickets}
                requestID={props.requestID}
                settingsID={'group'}
                cacheID={props.cacheID}
            />
        </div>

    )
}

export default GroupedTicketResults;