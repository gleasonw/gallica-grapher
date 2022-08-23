import React, {useContext} from 'react';
import {GraphSettingsContext} from "./GraphSettingsContext";

function TicketLabel(props){
    return(
        <div className='ticketLabel'>
            <TicketTermRow terms={props.terms}/>
            <TicketPaperRow papers={props.papers}/>
            <TicketDateRow dateRange={props.dateRange}/>
        </div>
    )
}

function TicketTermRow(props){
    const quotedTerms = props.terms.map(
        term => "'" + term + "'"
    ).join(', ')
    return(renderRow(quotedTerms))
}
function TicketPaperRow(props){
    const papers = props.papers
    const paperNames = []
    papers.map(paperAndCode => (
        paperNames.push(paperAndCode['title'])
    ));
    return(renderRow(paperNames))
}
function renderRow(items){
    if(items.length !== 0){
        return(
            <div className='bubbleText'>
                {items}
            </div>
        )
    }
}
function TicketDateRow(props){
    const dateRange = props.dateRange
    if(dateRange){
        return(
            <div className='bubbleText'>
                {dateRange[0]} - {dateRange[1]}
            </div>
        )
    }
}

export default TicketLabel;