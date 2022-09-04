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
                bubblesLabel={'Graph occurrences of these terms:'}
                onClick={props.deleteTermBubble}
            />
            <input
                type="text"
                value={termInput}
                name="updatedTerms"
                placeholder="Type here and press 'enter'..."
                onChange={handleTermChange}
                onKeyDown={handleKeyDown}
                autoComplete="off"
            />
        </TextInputBubble>
    )
}