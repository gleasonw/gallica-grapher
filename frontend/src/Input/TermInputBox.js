import React from "react";
import TextInputBubble from "./TextInputBubble";

export function TermInputBox(props) {

    function handleKeyDown(event) {
        if (event.key === 'Enter') {
            props.onEnterPress(event)
        }
    }

    return (
        <TextInputBubble noTermsReminder={props.noTermsReminder}>
            <input
                type="text"
                value={props.termInput}
                name="updatedTerms"
                placeholder={props.noTermsReminder ? "ENTER A TERM" : "Enter a search term"}
                onChange={props.handleTermChange}
                onKeyDown={handleKeyDown}
                autoComplete="off"
            />
        </TextInputBubble>
    )
}