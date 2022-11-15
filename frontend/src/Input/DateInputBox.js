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
        </StyledDateInputs>
    )
}

const StyledDateInputs = styled.div`
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    margin: 0.5rem 0;
    font-size: 30px;
    gap: 0.5rem;
    width: auto;
   `;