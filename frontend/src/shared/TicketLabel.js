import React from 'react';
import InlineBubble from './InlineBubble';
import styled from 'styled-components';

//TODO: blurbs should be components

function TicketLabel(props){
    const termBlurb = <TermBlurb terms={props.terms}></TermBlurb>
    const paperBlurb = <PaperBlurb papers={props.papers}></PaperBlurb>
    const dateBlurb = <DateBlurb dateRange={props.dateRange}></DateBlurb>
    return(
        <div className='ticketLabel'>
            Occurrences of {termBlurb} in {paperBlurb} from {dateBlurb}
        </div>
    )
}

function TermBlurb(props){
    return renderItemsToBlurb(props.terms)
    
}

function PaperBlurb(props){
    const papers = props.papers
    let paperNames = []
    papers.map(paperAndCode => (
        paperNames.push(paperAndCode['title'])
    ));
    if (paperNames.length === 0){
        paperNames = ['all papers']
    }
    return renderItemsToBlurb(paperNames)
   
}

function DateBlurb(props){
    const dateRange = props.dateRange
    const rangeString = `${dateRange[0]} to ${dateRange[1]}`
    return <InlineBubble selected={true}>
        <BlurbText>{rangeString}</BlurbText>
    </InlineBubble>
}

function renderItemsToBlurb(items){
    let blurb;
    if(items.length > 1){
        const highestIndex = getHighestIndexTo28CharactersCombined(items)
        const numItemsAfterHighest = items.length - highestIndex - 1
        const itemsToShow = items.slice(0, highestIndex + 1)
        const quotedItems = itemsToShow.map(item => `"${item}"`)
        const commaSeparatedItems = quotedItems.join(', ')
        blurb =
                numItemsAfterHighest > 0 ?
                    <span>
                    <BlurbText>{commaSeparatedItems}</BlurbText> + {numItemsAfterHighest} more
                    </span>
                :
                    <span>
                    <BlurbText>{commaSeparatedItems}</BlurbText>
                    </span>
    }else{
        blurb = <BlurbText>"{items[0]}"</BlurbText>
    }
    return <InlineBubble selected={true}>{blurb}</InlineBubble>
}

function getHighestIndexTo28CharactersCombined(items){
    let combinedLength = 0
    let highestIndex = 0
    items.map((item, index) => {
        combinedLength += item.length
        if(combinedLength < 28){
            highestIndex = index
        }
    })
    return highestIndex
}

const BlurbText = styled.span`
    max-width: 110px;
    max-height: 180px;
    overflow: hidden;
    text-overflow: ellipsis;
`

export default TicketLabel;