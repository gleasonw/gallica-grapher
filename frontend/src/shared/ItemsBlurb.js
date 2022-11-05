import React from 'react';
import {ExpandableBlurbControl} from "./ExpandableBlurbControl";
import {BlurbText} from "./BlurbText";

export function PaperBlurb(props){
    const titles = getPaperNames(props.papers)
    return props.papers.length > 0 ? <TermsBlurb terms={titles}/> : <BlurbText>all papers</BlurbText>
}

export function DateBlurb(props){
    const dateString = `${props.dateRange[0]} and ${props.dateRange[1]}`
    return <BlurbText>{dateString}</BlurbText>
}

export function TermsBlurb(props) {
    const highestIndexBefore28Characters = getHighestIndexBeforeLimitCharactersCombined(props.terms)
    const numItemsRemaining = props.terms.length - highestIndexBefore28Characters - 1
    if (numItemsRemaining > 0) {
        return generateExpandableBlurb(
            props.terms,
            highestIndexBefore28Characters,
            numItemsRemaining
        )
    } else {
        return generateFixedBlurb(props.terms)
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