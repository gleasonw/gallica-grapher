import React from 'react';
import {TicketProgressContainer} from "./TicketProgressContainer";


function RunningQueriesUI(props) {

    return(
        <TicketProgressContainer
            tickets={props.tickets}
            requestid={props.taskID}
            onFinish={props.onFinish}
            onTooManyRecords={props.onTooManyRecords}
        />
    )
}

export default RunningQueriesUI;