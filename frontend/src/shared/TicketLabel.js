import React from 'react';
import {ExpandableBlurbControl} from "./ExpandableBlurbControl";
import {BlurbText} from "./BlurbText";

function TicketLabel(props){
    const paperNames = getPaperNames(props.papers)
    const dateString = `${props.dateRange[0]} to ${props.dateRange[1]}`
    return(
        <div className='ticketLabel'>
            <span>Occurrences of</span>
            {generateBlurb(props.terms)}
            <span>in</span>
            {generateBlurb(paperNames)}
            <span>from</span>
            <BlurbText>{dateString}</BlurbText>
        </div>
    )
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
    let shortenedItemString = quotedItems.slice(0, indexToStopAt + 1)
    const itemString = quotedItems.join(', ')
    shortenedItemString = shortenedItemString.join(', ')
    console.log(items)
    return(
        <ExpandableBlurbControl
            numItemsRemaining={numItemsRemaining}
            allItems={itemString}
            shortenedItems={shortenedItemString}
            items={items}
        />
    )
}


function generateFixedBlurb(items){
    const quotedItems = items.map(item => `"${item}"`)
    const commaSeparatedItems = quotedItems.join(', ')
    return <BlurbText>{commaSeparatedItems}</BlurbText>
}

function getPaperNames(papers){
    if(papers.length === 0){
        return('all papers')
    }else{
        let paperNames = []
        papers.map(paperAndCode => (
            paperNames.push(paperAndCode['title'])
        ));
        return paperNames
    }
}

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
