import {ShadowedFocusInput} from "../shared/ShadowedFocusInput";
import React from "react";
import styled from 'styled-components';

export function DateInputBox(props) {
    return (
        <StyledDateInputs>
            <StyledDateWidth>
                <ShadowedFocusInput
                    selected
                    type={'text'}
                    value={props.startYear}
                    id={'lowYear'}
                    className={'dateInput'}
                    placeholder={1880}
                    onChange={(e) => props.onStartYearChange(e.target.value)}
                />
            </StyledDateWidth>
            and
            <StyledDateWidth>
                <ShadowedFocusInput
                    selected
                    type={'text'}
                    value={props.endYear}
                    id={'highYear'}
                    className={'dateInput'}
                    placeholder={1900}
                    onChange={(e) => props.onEndYearChange(e.target.value)}
                />
            </StyledDateWidth>
        </StyledDateInputs>
    )
}

const StyledDateInputs = styled.div`
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    padding: 0.5rem;
    padding-left: 1rem;
    padding-right: 1rem;
    gap: 1rem;
    margin: 0.5rem 0;
    font-size: 1.5rem;
    flex-wrap: wrap;
   `;

const StyledDateWidth = styled.div`
    max-width: 200px;
    `;