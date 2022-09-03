import TextInputBubble from "./TextInputBubble";
import React from "react";

export function DateInputBox(props) {
    return (
        <div className='dateInputs'>
            <TextInputBubble>
                <input
                    id="lowYear"
                    type='text'
                    value={props.lowYear}
                    onChange={props.onLowDateChange}
                    placeholder={props.minYearPlaceholder}
                />
            </TextInputBubble>
            to
            <TextInputBubble>
                <input
                    id="highYear"
                    type='text'
                    value={props.highYear}
                    onChange={props.onHighDateChange}
                    placeholder={props.maxYearPlaceholder}
                />
            </TextInputBubble>
        </div>
    )
}