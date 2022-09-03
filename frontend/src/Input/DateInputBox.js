import DateInputBubble from './DateInputBubble';
import React from "react";

export function DateInputBox(props) {
    return (
        <div className='dateInputs'>
            <DateInputBubble selected={props.selected}>
                <input
                    id="lowYear"
                    type='text'
                    name='lowYear'
                    value={props.lowYear}
                    onChange={props.onLowDateChange}
                    placeholder={props.minYearPlaceholder}
                />
            </DateInputBubble>
            and
            <DateInputBubble selected={props.selected}>
                <input
                    id="highYear"
                    type='text'
                    name='highYear'
                    value={props.highYear}
                    onChange={props.onHighDateChange}
                    placeholder={props.maxYearPlaceholder}
                />
            </DateInputBubble>
            .
        </div>
    )
}