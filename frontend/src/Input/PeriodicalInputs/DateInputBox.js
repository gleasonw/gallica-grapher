import InlineBubble from '../../shared/InlineBubble';
import React from "react";

export function DateInputBox(props) {
    return (
        <div className='dateInputs'>
            <InlineBubble selected={props.selected}>
                <input
                    id="lowYear"
                    type='text'
                    name='lowYear'
                    className='dateInput'
                    value={props.lowYear}
                    onChange={props.onLowDateChange}
                    placeholder={props.minYearPlaceholder}
                />
            </InlineBubble>
            and
            <InlineBubble selected={props.selected}>
                <input
                    id="highYear"
                    type='text'
                    name='highYear'
                    className='dateInput'
                    value={props.highYear}
                    onChange={props.onHighDateChange}
                    placeholder={props.maxYearPlaceholder}
                />
            </InlineBubble>
            .
        </div>
    )
}