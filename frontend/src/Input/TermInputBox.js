import React from "react";
import TextInputBubble from "./TextInputBubble";

export function TermInputBox(props) {

    function handleKeyDown(event) {
        if (event.key === 'Enter') {
            props.onEnterPress(event)
        }
    }

    return (
        <TextInputBubble>
            <input
                type="text"
                value={props.termInput}
                name="updatedTerms"
                placeholder="Enter a search term"
                onChange={props.handleTermChange}
                onKeyDown={handleKeyDown}
                autoComplete="off"
            />
        </TextInputBubble>
    )
}