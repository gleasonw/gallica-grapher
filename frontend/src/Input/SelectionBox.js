import React from "react";
import {SelectionBubble} from "../shared/SelectionBubble";

export function SelectionBox(props) {
    const bubbles = props.items ?
        props.items.map((item, index) => (
            <SelectionBubble
                onClick={() => props.onClick(index)}
                key={index}
            >
                {item}
            </SelectionBubble>
        )) :
        <SelectionBubble></SelectionBubble>

    return (
        <div className='bubblesContainer'>
            {bubbles}
        </div>
    )
}

