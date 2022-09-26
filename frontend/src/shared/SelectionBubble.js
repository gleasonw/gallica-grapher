import LesserButton from "./LesserButton";
import RemoveCircleIcon from "@mui/icons-material/RemoveCircle";
import React from "react";

export function SelectionBubble(props) {
    return (
        <LesserButton
            className='bubbleItem'
            type='button'
            onClick={props.onClick}
        >
            <span className='bubbleText'>
                {props.children}
            </span>
            <RemoveCircleIcon/>
        </LesserButton>
    )
}