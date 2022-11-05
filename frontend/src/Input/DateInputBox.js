import {ShadowedFocusInput} from "../shared/ShadowedFocusInput";
import React from "react";
import styled from 'styled-components';

export function DateInputBox(props) {
    return (
        <StyledDateInputs>
            <ShadowedFocusInput
                selected
                type={'text'}
                value={props.startYear}
                id={'lowYear'}
                className={'dateInput'}
                placeholder={1880}
                onChange={(e) => props.onStartYearChange(e.target.value)}
            />
            /
            <ShadowedFocusInput
                selected
                type={'text'}
                value={props.startMonth}
                id={'month'}
                className={'dateInput'}
                placeholder={1}
                onChange={(e) => props.onStartMonthChange(e.target.value)}
            />
            /
            <ShadowedFocusInput
                selected
                type={'text'}
                value={props.startDay}
                id={'day'}
                className={'dateInput'}
                placeholder={1}
                onChange={(e) => props.onStartDayChange(e.target.value)}
            />

            and

            <ShadowedFocusInput
                selected
                type={'text'}
                value={props.endYear}
                id={'highYear'}
                className={'dateInput'}
                placeholder={1900}
                onChange={(e) => props.onEndYearChange(e.target.value)}
            />
            /
            <ShadowedFocusInput
                selected
                type={'text'}
                value={props.endMonth}
                id={'endMonth'}
                className={'dateInput'}
                placeholder={12}
                onChange={(e) => props.onEndMonthChange(e.target.value)}
            />
            /
            <ShadowedFocusInput
                selected
                type={'text'}
                value={props.endDay}
                id={'endDay'}
                className={'dateInput'}
                placeholder={31}
                onChange={(e) => props.onEndDayChange(e.target.value)}
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