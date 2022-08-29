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
    return (
        <div>
            Ngrams: {renderRow(props.terms)}
        </div>
        )
}
function TicketPaperRow(props){
    const papers = props.papers
    const paperNames = []
    papers.map(paperAndCode => (
        paperNames.push(paperAndCode['title'])
    ));
    return(<div>
        In Periodicals: {renderRow(paperNames)}
    </div>
    )
}
function renderRow(items){
    const quotedItems= items.map(
        term => "'" + term + "'"
    ).join(', ')
    if(items.length !== 0){
        return(
            <div className='bubbleText'>
                {quotedItems}
            </div>
        )
    }
}
function TicketDateRow(props){
    const dateRange = props.dateRange
    if(dateRange){
        return(
            <div>
                Over range:
                <div className={'bubbleText'}>
                    {dateRange[0]} to {dateRange[1]}
                </div>
            </div>
        )
    }
}

export default TicketLabel;