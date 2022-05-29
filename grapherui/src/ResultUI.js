import React, {useState} from 'react';

function ResultUI(){
    const [JSONGraphDataForTickets, setJSONGraphDataForTickets] = useState([]);
    const [grouped, setGrouped] = useState(true);
    if(grouped){
        return(
            <div className='resultUI'>
                <input type='button' className='graphGroupButton'/>
                <GroupedTicketLabelBar/>
                <GroupedGraph/>
                <GroupedTicketInfoBar/>
            </div>
        )
    }else{
        return(
            <div className='resultUI'>
                <input type='button' className='graphGroupButton'/>
                <TicketResultContainer/>
            </div>
        )
    }

}
function GroupedTicketLabelBar() {
    return null;
}

function GroupedGraph() {
    return null;
}

function GroupedTicketInfoBar() {
    return null;
}

function TicketResultContainer() {
    return (
        <div>
            <TicketResult/>
        </div>
    )
}
function TicketResult() {
    return null;
}

export default ResultUI;