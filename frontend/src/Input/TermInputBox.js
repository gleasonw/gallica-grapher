import React, {useState} from "react";
import TextInputBubble from "./TextInputBubble";
import {SelectionBox} from "./SelectionBox";

export function TermInputBox(props) {
    const [termInput, setTermInput] = useState('');

    function handleTermChange(event) {
        setTermInput(event.target.value)
    }

    function handleKeyDown(event) {
        if (event.key === 'Enter') {
            props.onKeyDown(event);
            setTermInput('');
        }
    }

    return (
        <TextInputBubble>
            <SelectionBox
                items={props.selectedTerms}
                onClick={props.deleteTermBubble}
            />
            <input
                type="text"
                value={termInput}
                name="updatedTerms"
                placeholder="Enter a search term"
                onChange={handleTermChange}
                onKeyDown={handleKeyDown}
                autoComplete="off"
            />
        </TextInputBubble>
    )
}