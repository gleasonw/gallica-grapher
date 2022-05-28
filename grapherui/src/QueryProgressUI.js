import React,{useState, useEffect} from 'react';
import ProgressBar from 'react-bootstrap/ProgressBar';
import TicketInfo from "./TicketInfo";

function QueryProgressUI(props) {
    //TODO: Lift state up, receive request tickets as prop
    const [ticketProgressPercents, setProgressPercents] = useState([]);
    return(
        <div className='queryProgressUI'>
            <TicketProgressBox/>
        </div>
    )
}
function TicketProgressBox(props){
    return(
        <div className='ticketProgressBox'>
            <TicketInfo
                terms={['hello']}
                papers={[{'code': '1234123', 'paper':'neat'}]}
                dateRange={[1989,2001]}
            />
            <ProgressBar
                animated
                now={45}
            />
        </div>
    )
}

export default QueryProgressUI;