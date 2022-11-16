import {StyledInputAndLabel, StyledSelect} from "../shared/StyledSelect";
import {ShadowedFocusInput} from "../shared/ShadowedFocusInput";
import React from "react";
import styled from "styled-components";
import OutsideAlerter from "../shared/OutsideAlerter";
import {DateSelect} from "../shared/DateSelect";

export function FilterOptions(props) {
    return (
        <FilterOptionsDisplaySwitch
            compact={props.compact}
            show={props.show}
            onOutsidePopupClick={props.onOutsidePopupClick}
        >
            <DateSelect
                year={props.year}
                onYearChange={props.onYearChange}
                month={props.month}
                onMonthChange={props.onMonthChange}
                day={props.day}
                onDayChange={props.onDayChange}
            />
            <StyledInputAndLabel>
                <label htmlFor='ticket'>Ticket</label>
                <StyledSelect
                    value={!!props.selectedTicket ? props.selectedTicket : ''}
                    id={'ticket'}
                    onChange={
                        (e) => props.onSelectedTicketChange(e.target.value)
                    }
                >
                    <option value={''}>All</option>
                    {Object.keys(props.tickets).map((ticket) => {
                        const args = props.tickets[ticket];
                        const terms = args.terms;
                        const linkTerm = args.linkTerm;
                        return (
                            <option value={ticket}>
                                {terms}
                                {!!linkTerm && ` linked to ${linkTerm}`}
                            </option>
                        )
                    })}
                </StyledSelect>
            </StyledInputAndLabel>
            {!props.isGallicaGrouped &&
                <StyledInputAndLabel>
                    <label htmlFor='periodical'>Periodical</label>
                    <ShadowedFocusInput
                        type={'text'}
                        selected
                        value={!!props.periodical ? props.periodical : ''}
                        id={'periodical'}
                        placeholder={'Enter a periodical to filter'}
                        onChange={
                            (e) => props.onPeriodicalChange(e.target.value)
                        }
                    />
                </StyledInputAndLabel>
            }
        </FilterOptionsDisplaySwitch>
    )
}

function FilterOptionsDisplaySwitch(props){
    if(props.compact){
        return (
            <OutsideAlerter doThis={() => props.onOutsidePopupClick()}>
                <StyledOptionsFilterPop show={props.show}>
                    {props.children}
                </StyledOptionsFilterPop>
            </OutsideAlerter>
        )
    }else{
        return (
            <StyledFullOptions>
                {props.children}
            </StyledFullOptions>
        )
    }
}

const StyledFullOptions = styled.div`
    display: flex;
    flex-direction: column;
    box-shadow: 1px 3px 5px 0 #ddd;
    flex: none;
    padding: 16px;
    border-radius: 3px;
`;

const StyledOptionsFilterPop = styled.div`
    display: ${props => props.show ? 'flex' : 'none'};
    position: absolute;
    left: 0;
    right: 0;
    margin-left: auto;
    margin-right: auto;
    flex-direction: column;
    box-shadow: 1px 3px 5px 0 #ddd;
    flex: none;
    padding: 16px;
    border-radius: 3px;
    align-items: stretch;
    z-index: 1;
    background-color: white;
    `;