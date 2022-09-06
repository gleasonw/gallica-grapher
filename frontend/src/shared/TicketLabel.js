import React from 'react';
import LesserButton from "./LesserButton";

function TicketLabel(props){
    return(
        <div className='ticketLabel'>
            <TicketTermRow terms={props.terms}/>
            {props.papers.length > 0 && <TicketPaperRow papers={props.papers}/>}
            <TicketDateRow dateRange={props.dateRange}/>
        </div>
    )
}

function TicketTermRow(props){
    const quotedTerms = wrapItemsInBubbles(props.terms)
    return renderRow(quotedTerms, 'Ngrams:')
}
function TicketPaperRow(props){
    const papers = props.papers
    const paperNames = []
    papers.map(paperAndCode => (
        paperNames.push(paperAndCode['title'])
    ));
    const quotedItems= wrapItemsInBubbles(paperNames)
    console.log(quotedItems)
    return renderRow(quotedItems, 'In papers:')
}
function wrapItemsInBubbles(items){
    return items.map((item) => (
        <LesserButton>{item}</LesserButton>
    ));
}
function renderRow(item, label){
    if(item){
        return(
            <section className={'ticketItems'}>
                <h3 className={'ticketRowLabel'}>
                    {label}
                </h3>
                <div className={'bubblesContainer'}>
                    {item}
                </div>
            </section>
        )
    }
}
function TicketDateRow(props){
    const dateRange = props.dateRange
    const rangeString = dateRange[0] + ' to ' + dateRange[1]
    return renderRow(rangeString, 'Over range:')
}

export default TicketLabel;