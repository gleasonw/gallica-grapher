import {ShadowedFocusInput} from "../shared/ShadowedFocusInput";
import React from "react";

export function DateInputBox(props) {
    return (
        <div className='dateInputs'>
            <ShadowedFocusInput
                selected
                type={'text'}
                value={props.startDate}
                id={'lowYear'}
                className={'dateInput'}
                placeholder={props.minYearPlaceholder}
                onChange={props.onstartDateChange}
            />
            and
            <ShadowedFocusInput
                selected
                type={'text'}
                value={props.endDate}
                id={'highYear'}
                className={'dateInput'}
                placeholder={props.maxYearPlaceholder}
                onChange={props.onendDateChange}
            />
        </div>
    )
}