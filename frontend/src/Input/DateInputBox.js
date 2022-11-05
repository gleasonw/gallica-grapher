import {ShadowedFocusInput} from "../shared/ShadowedFocusInput";
import React from "react";
import styled from 'styled-components';

export function DateInputBox(props) {
    return (
        <StyledDateInputs>
            <ShadowedFocusInput
                selected
                type={'text'}
                value={props.startDate}
                id={'lowYear'}
                className={'dateInput'}
                placeholder={props.minYearPlaceholder}
                onChange={props.onstartDateChange}
            />
            /
            <ShadowedFocusInput
                selected
                type={'text'}
                value={props.startMonth}
                id={'month'}
                className={'dateInput'}
                placeholder={props.monthPlaceholder}
                onChange={props.onMonthChange}
            />
            /
            <ShadowedFocusInput
                selected
                type={'text'}
                value={props.startDay}
                id={'day'}
                className={'dateInput'}
                placeholder={props.dayPlaceholder}
                onChange={props.onDayChange}
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
            /
            <ShadowedFocusInput
                selected
                type={'text'}
                value={props.endMonth}
                id={'endMonth'}
                className={'dateInput'}
                placeholder={props.endMonthPlaceholder}
                onChange={props.onEndMonthChange}
            />
            /
            <ShadowedFocusInput
                selected
                type={'text'}
                value={props.endDay}
                id={'endDay'}
                className={'dateInput'}
                placeholder={props.endDayPlaceholder}
                onChange={props.onEndDayChange}
            />
        </StyledDateInputs>
    )
}

const StyledDateInputs = styled.div`
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    margin: 0.5rem 0;
    font-size: 1.5rem;
    gap: 0.5rem;
   `;