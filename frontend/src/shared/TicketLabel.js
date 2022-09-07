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
            Occurrences of {termBlurb} in {paperBlurb} from {dateBlurb}
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
            <InlineBubble selected={true}>
                all papers
            </InlineBubble>
        )
    }else{
        let paperNames = []
        papers.map(paperAndCode => (
            paperNames.push(paperAndCode['title'])
        ));
        return (
            <div className={props.className}>
                {generateBlurb(paperNames)}
            </div>
        )
    }
}

function DateBlurb(props){
    const dateRange = props.dateRange
    const rangeString = `${dateRange[0]} to ${dateRange[1]}`
    return <BlurbText>{rangeString}</BlurbText>
}

function generateBlurb(items){
    const highestIndexBefore28Characters = getHighestIndexTo28CharactersCombined(items)
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

function generateExpandableBlurb(items, indexToStopAt, numItemsRemaining){
    const quotedItems = items.map(item => `"${item}"`)
    const allItems = quotedItems.join(', ')
    const shortenedItems = allItems.slice(0, indexToStopAt + 1)
    return(
        <ExpandableBlurbControl
            numItemsRemaining={numItemsRemaining}
            allItems={allItems}
            shortenedItems={shortenedItems}
        />
    )
}

function generateFixedBlurb(items){
    const quotedItems = items.map(item => `"${item}"`)
    const commaSeparatedItems = quotedItems.join(', ')
    return <BlurbText>{commaSeparatedItems}</BlurbText>
}


const BlurbText = styled.span`
    max-width: 110px;
    max-height: 180px;
    overflow: hidden;
    text-overflow: ellipsis;
    padding: 10px;
`

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
                <StyledExpandedText children={props.allItems}/> :
                <BlurbText>
                    {props.shortenedItems} + {props.numItemsRemaining} more
                </BlurbText>
            }
            {arrow}
        </button>
    )
}

const StyledExpandedText = styled.section`
    width: 100%;
    height: 100%;
`;


export default TicketLabel;
