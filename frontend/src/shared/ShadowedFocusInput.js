import React from 'react';
import InlineBubble from "./InlineBubble";

export function ShadowedFocusInput(props) {
    const [focus, setFocus] = React.useState(false);
    return (
        <InlineBubble focus={focus} selected={props.selected}>
            <input
                className={props.className}
                type={props.type}
                value={props.value}
                name={props.name}
                placeholder={props.placeholder}
                onChange={props.onChange}
                onKeyUp={props.onKeyUp}
                autoComplete="off"
                onFocus={() => setFocus(true)}
                onBlur={() => setFocus(false)}
            />
        </InlineBubble>
    )
}