import React from 'react';
import {ExpandableBlurbControl} from "./ExpandableBlurbControl";
import {BlurbText} from "./BlurbText";

export default function ItemsBlurb(props){
    if(props.papers){
        return makePaperBlurb(props.papers)
    }else if(props.terms){
        return generateBlurb(props.terms)
    }else if(props.dateRange){
        const dateString = `${props.dateRange[0]} to ${props.dateRange[1]}`
        return <BlurbText>{dateString}</BlurbText>
    }else{
        return null
    }
}

export function generateBlurb(items) {
    const highestIndexBefore28Characters = getHighestIndexBeforeLimitCharactersCombined(items)
    const numItemsRemaining = items.length - highestIndexBefore28Characters - 1
    if (numItemsRemaining > 0) {
        return generateExpandableBlurb(
            items,
            highestIndexBefore28Characters,
            numItemsRemaining
        )
    } else {
        return generateFixedBlurb(items)
    }
}

function generateExpandableBlurb(items, indexToStopAt, numItemsRemaining) {
    const quotedItems = items.map(item => `"${item}"`)
    let shortenedItemString = quotedItems.slice(0, indexToStopAt + 1)
    shortenedItemString = shortenedItemString.join(', ')
    return (
        <ExpandableBlurbControl
            numItemsRemaining={numItemsRemaining}
            shortenedItems={shortenedItemString}
            items={items.slice(indexToStopAt + 1, items.length)}
        />
    )
}

function generateFixedBlurb(items) {
    const quotedItems = items.map(item => `"${item}"`)
    const commaSeparatedItems = quotedItems.join(', ')
    return <BlurbText>{commaSeparatedItems}</BlurbText>
}

export function makePaperBlurb(papers) {
    const titles = getPaperNames(papers)
    return papers.length > 0 ? generateBlurb(titles) : <BlurbText>all papers</BlurbText>
}

function getPaperNames(papers) {
    let paperNames = []
    papers.map(paperAndCode => (
        paperNames.push(paperAndCode['title'])
    ));
    return paperNames
}

function getHighestIndexBeforeLimitCharactersCombined(items) {
    let combinedLength = 0
    let highestIndex = 0
    items.map((item, index) => {
        combinedLength += item.length
        if (combinedLength < 15) {
            highestIndex = index
        } else {
            return highestIndex
        }
    })
    return highestIndex
}