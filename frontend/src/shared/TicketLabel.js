import React from 'react';
import InlineBubble from './InlineBubble';

//TODO: blurbs should be components

function TicketLabel(props){
    return(
        <div className='ticketLabel'>
            Occurrences of {TermBlurb(props)} in {PaperBlurb(props)} periodicals from {DateBlurb(props)}
        </div>
    )
}

function TermBlurb(props){
    return renderItemsToBlurb(props.terms)
    
}

function PaperBlurb(props){
    const papers = props.papers
    const paperNames = []
    papers.map(paperAndCode => (
        paperNames.push(paperAndCode['title'])
    ));
    return renderItemsToBlurb(paperNames)
   
}

function DateBlurb(props){
    const dateRange = props.dateRange
    const rangeString = `${dateRange[0]} to ${dateRange[1]}`
    return <span>{rangeString}</span>
}

function renderItemsToBlurb(items){
    console.log(items)
    let blurb;
    if(items.length > 1){
        const numItemsAfterFirst = items.length - 1
        blurb = <span>

            <span>"{items[0]}"</span> + {numItemsAfterFirst} more
        </span>
    }else{
        blurb = <span>"{items[0]}"</span>
    }
    return <InlineBubble selected={true}>{blurb}</InlineBubble>


}

export default TicketLabel;