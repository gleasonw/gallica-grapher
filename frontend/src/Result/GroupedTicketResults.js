import React, {useContext, useState} from "react";
import ClassicUIBox from "../shared/ClassicUIBox";
import GroupedTicketLabel from "./GroupedTicketLabel";
import RecordsViewer from "./RecordsViewer";

export function GroupedTicketResults(props) {
    return (
        <ClassicUIBox>
            <GroupedTicketLabel tickets={props.tickets}/>
            <RecordsViewer
                tickets={props.tickets}
                requestID={props.requestID}
            />
        </ClassicUIBox>

    )
}

export default GroupedTicketResults;