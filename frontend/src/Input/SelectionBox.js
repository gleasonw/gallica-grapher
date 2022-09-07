import React from "react";
import LesserButton from '../shared/LesserButton';
import RemoveCircleIcon from '@mui/icons-material/RemoveCircle';

export function SelectionBox(props) {
    const bubbles = props.items ?
        props.items.map((item, index) => (
            <SelectionBubble
                onClick={() => props.onClick(index)}
                key={index}
                item={item}
            />
        )) :
        <SelectionBubble></SelectionBubble>

    return (
        <div className='bubblesContainer'>
            {bubbles}
        </div>
    )
}

function SelectionBubble(props) {
    return (
        <LesserButton
            className='bubbleItem'
            type='button'
            onClick={props.onClick}
        >
            <span className='bubbleText'>
                {props.item}
            </span>
            <RemoveCircleIcon/>
        </LesserButton>
    )
}