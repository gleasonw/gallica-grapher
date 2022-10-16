import {ShadowedFocusInput} from "../shared/ShadowedFocusInput";
import React from "react";

export function DateInputBox(props) {
    return (
        <div className='dateInputs'>
            <ShadowedFocusInput
                selected
                type={'text'}
                value={props.startYear}
                id={'lowYear'}
                className={'dateInput'}
                placeholder={props.minYearPlaceholder}
                onChange={props.onStartYearChange}
            />
            and
            <ShadowedFocusInput
                selected
                type={'text'}
                value={props.endYear}
                id={'highYear'}
                className={'dateInput'}
                placeholder={props.maxYearPlaceholder}
                onChange={props.onEndYearChange}
            />
        </div>
    )
}