import React from "react";
import TextInputBubble from "./TextInputBubble";


export function TermInputBox(props) {
    const [focus, setFocus] = React.useState(false);

    function handleKeyDown(event) {
        if (event.key === 'Enter') {
            props.onEnterPress(event)
        }
    }

    return (
        <div>
            <TextInputBubble
                noTermsReminder={props.noTermsReminder}
                focus={focus}
                borderRadius={'10px 10px 10px 0px'}
            >
                <input
                    autoFocus
                    type="text"
                    value={props.termInput}
                    name="updatedTerms"
                    placeholder={props.noTermsReminder ? "Please enter a word" : "Enter a word"}
                    onChange={props.handleTermChange}
                    onKeyDown={handleKeyDown}
                    autoComplete="off"
                    onFocus={() => setFocus(true)}
                    onBlur={() => setFocus(false)}
                />
            </TextInputBubble>
        </div>
    )
}