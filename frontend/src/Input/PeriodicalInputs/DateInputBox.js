import InlineBubble from '../../shared/InlineBubble';
import {ShadowedFocusInput} from "../../shared/ShadowedFocusInput";
import React from "react";

export function DateInputBox(props) {
    return (
        <div className='dateInputs'>
            <ShadowedFocusInput
                selected={props.selected}
                type={'text'}
                value={props.lowYear}
                id={'lowYear'}
                className={'dateInput'}
                placeholder={props.minYearPlaceholder}
                onChange={props.onLowDateChange}
            />
            and
            <ShadowedFocusInput
                selected={props.selected}
                type={'text'}
                value={props.highYear}
                id={'highYear'}
                className={'dateInput'}
                placeholder={props.maxYearPlaceholder}
                onChange={props.onHighDateChange}
            />
            .
        </div>
    )
}