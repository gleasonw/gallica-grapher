import React,{useState, useEffect} from 'react';
import ProgressBar from 'react-bootstrap/ProgressBar';

function QueryProgressUI(props) {
    return(
        <div className='queryProgressUI'>
            <TicketProgressBox/>
        </div>
    )
}
function TicketProgressBox(props){
    return(
        <div className='ticketProgressBox'>
            <TicketRow/>
            <ProgressBar
                animated
                now={45}
            />
        </div>
    )

}
function TicketRow(props){
    return(
        <div className='ticketRow'>

        </div>
    )
}
export default QueryProgressUI;