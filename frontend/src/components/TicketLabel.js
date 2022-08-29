import React from 'react';

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
    const quotedTerms = addQuotesAndCommasAroundItems(props.terms)
    return renderRow(quotedTerms, 'Ngrams:')
}
function TicketPaperRow(props){
    const papers = props.papers
    const paperNames = []
    papers.map(paperAndCode => (
        paperNames.push(paperAndCode['title'])
    ));
    const quotedItems= addQuotesAndCommasAroundItems(paperNames)
    return renderRow(quotedItems, 'In papers:')
}
function addQuotesAndCommasAroundItems(items){
    return items.map(
        term => "'" + term + "'"
    ).join(', ')
}
function renderRow(item, label){
    if(item){
        return(
            <div className={'ticketRow'}>
                <span className={'ticketRowLabel'}>{label}</span>
                <div className={'bubblesContainer'}>
                    <div className='bubbleItem'>
                        <div className={'bubbleText'}>
                            {item}
                        </div>
                    </div>

                </div>
            </div>
        )
    }
}
function TicketDateRow(props){
    const dateRange = props.dateRange
    const rangeString = dateRange[0] + ' to ' + dateRange[1]
    return renderRow(rangeString, 'Over range:')
}

export default TicketLabel;