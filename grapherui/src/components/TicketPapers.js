import React from "react";

export function TicketPapers(props) {
    return (
        <div className='ticketStats'>
            <ul>
                <li>Le Petit journal</li>
                <li>Le Figaro</li>
            </ul>
            <button className='downloadButton' onClick={props.onClick}>
                {props.text}
            </button>
        </div>
    )
}

export default TicketPapers;