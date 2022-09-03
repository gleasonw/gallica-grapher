import React from 'react';
import {TicketProgressContainer} from "./TicketProgressContainer";


function RunningQueriesUI(props) {
    return(
        <div>
            <TicketProgressContainer
                tickets={props.tickets}
                requestid={props.requestID}
                onFinish={props.onFinish}
                onTooManyRecords={props.onTooManyRecords}
            />
        </div>
    )
}

export default RunningQueriesUI;