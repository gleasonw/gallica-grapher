import React, {useState} from 'react';
import InlineBubble from './InlineBubble';
import styled from 'styled-components';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';

function TicketLabel(props){
    const termBlurb = <TermBlurb terms={props.terms}></TermBlurb>
    const paperBlurb = <PaperBlurb papers={props.papers}></PaperBlurb>
    const dateBlurb = <DateBlurb dateRange={props.dateRange}></DateBlurb>
    return(
        <div className='ticketLabel'>
            <span>Occurrences of</span>
            {termBlurb}
            <span>in</span>
            {paperBlurb}
            <span>from</span>
            {dateBlurb}
        </div>
    )
}

function TermBlurb(props){
    return (
        <div className={props.className}>
            {generateBlurb(props.terms)}
        </div>
    )

}

function PaperBlurb(props){
    const papers = props.papers
    if(papers.length === 0){
        return (
            <BlurbText>
                all papers
            </BlurbText>
        )
    }else{
        let paperNames = []
        papers.map(paperAndCode => (
            paperNames.push(paperAndCode['title'])
        ));
        return generateBlurb(paperNames)
    }
}

function DateBlurb(props){
    const dateRange = props.dateRange
    const rangeString = `${dateRange[0]} to ${dateRange[1]}`
    return <BlurbText>{rangeString}</BlurbText>
}

function generateBlurb(items){
    const highestIndexBefore28Characters = getHighestIndexBefore28CharactersCombined(items)
    const numItemsRemaining = items.length - highestIndexBefore28Characters - 1
    if(numItemsRemaining > 0){
        return generateExpandableBlurb(
            items,
            highestIndexBefore28Characters,
            numItemsRemaining
        )
    }else{
        return generateFixedBlurb(items)
    }
}

function generateExpandableBlurb(items, indexToStopAt, numItemsRemaining){
    const quotedItems = items.map(item => `"${item}"`)
    let shortenedItems = quotedItems.slice(0, indexToStopAt + 1)
    const allItems = quotedItems.join(', ')
    shortenedItems = shortenedItems.join(', ')
    return(
        <ExpandableBlurbControl
            numItemsRemaining={numItemsRemaining}
            allItems={allItems}
            shortenedItems={shortenedItems}
        />
    )
}


function ExpandableBlurbControl(props){
    const [expanded, setExpanded] = useState(false);
    const [arrow, setArrow] = useState(<ExpandMoreIcon/>);

    function handleClick(){
        setArrow(expanded ?
            <ExpandMoreIcon/> :
            <ExpandLessIcon/>
        )
        setExpanded(!expanded)
    }

    return(
        <button onClick={handleClick}>
            {expanded ?
                <BlurbText expanded={expanded}>{props.allItems}</BlurbText>:
                <span>
                    <BlurbText>
                        {props.shortenedItems}
                    </BlurbText>
                        + {props.numItemsRemaining} more
                </span>
            }
            {arrow}
        </button>
    )
}

function generateFixedBlurb(items){
    const quotedItems = items.map(item => `"${item}"`)
    const commaSeparatedItems = quotedItems.join(', ')
    return <BlurbText>{commaSeparatedItems}</BlurbText>
}

const BlurbText = styled.section`
    max-width: ${props => props.expanded ? '100%' : '150px'};
    max-height: 180px;
    overflow: ${props => props.expanded ? 'scroll' : 'hidden'};
    position: ${props => props.expanded ? 'absolute' : 'relative'};
    text-overflow: ellipsis;
    white-space: ${props => props.expanded ? 'wrap' : 'nowrap'};
    padding: 10px;
    border-radius: 3px;
    font-size: 20px;
    background: linear-gradient(to bottom, #f5f5f5 0%, #ededed 100%);
`

function getHighestIndexBefore28CharactersCombined(items) {
    let combinedLength = 0
    let highestIndex = 0
    items.map((item, index) => {
        combinedLength += item.length
        if (combinedLength < 28) {
            highestIndex = index
        } else {
            return highestIndex
        }
    })
    return highestIndex
}

export default TicketLabel;
