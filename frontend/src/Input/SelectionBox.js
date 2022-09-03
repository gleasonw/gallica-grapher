import React from "react";

export function SelectionBox(props) {
    return (
        <div className='bubblesContainer'>
            <h5 className='bubblesLabel'>
                {props.bubblesLabel}
            </h5>
            {props.items.map((item, index) => (
                <SelectionBubble
                    onClick={() => props.onClick(index)}
                    key={index}
                    item={item}
                />
            ))}
        </div>
    )
}

function SelectionBubble(props) {
    return (
        <button
            className='bubbleItem'
            type='button'
            onClick={props.onClick}
        >
            <span className='bubbleText'>
                {props.item}
            </span>
            <div className='bubbleDeleteButton'>
                <svg className="deleteButton" xmlns="http://www.w3.org/2000/svg" width="100" height="100"
                     viewBox="0 0 100 100">
                    <g transform="rotate(-45 50 50)">
                        <rect x="0" y="40" width="100" height="20"/>
                    </g>
                    <g transform="rotate(45 50 50)">
                        <rect x="0" y="40" width="100" height="20"/>
                    </g>
                </svg>
            </div>
        </button>
    )
}