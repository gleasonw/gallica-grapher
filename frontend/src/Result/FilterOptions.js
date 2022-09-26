import {StyledInputAndLabel, StyledSelect} from "../shared/StyledSelect";
import {ShadowedFocusInput} from "../shared/ShadowedFocusInput";
import React from "react";
import styled from "styled-components";
import OutsideAlerter from "../shared/OutsideAlerter";

export function FilterOptions(props) {
    return (
        <FilterOptionsDisplaySwitch
            compact={props.compact}
            show={props.show}
            onOutsidePopupClick={props.onOutsidePopupClick}
        >
            <StyledInputAndLabel>
                <label htmlFor='year'>Year</label>
                <ShadowedFocusInput
                    type={'number'}
                    selected
                    value={!!props.year ? props.year : ''}
                    id={'year'}
                    placeholder={'All'}
                    onChange={
                        (e) => props.onYearChange(e.target.value)
                    }
                />
            </StyledInputAndLabel>
            <StyledInputAndLabel>
                <label htmlFor='month'>Month</label>
                <StyledSelect
                    value={!!props.month ? props.month : ''}
                    id={'month'}
                    placeholder={'All'}
                    onChange={
                        (e) => props.onMonthChange(e.target.value)
                    }
                >
                    <option value={0}>All</option>
                    <option value={1}>January</option>
                    <option value={2}>February</option>
                    <option value={3}>March</option>
                    <option value={4}>April</option>
                    <option value={5}>May</option>
                    <option value={6}>June</option>
                    <option value={7}>July</option>
                    <option value={8}>August</option>
                    <option value={9}>September</option>
                    <option value={10}>October</option>
                    <option value={11}>November</option>
                    <option value={12}>December</option>
                </StyledSelect>
            </StyledInputAndLabel>
            <StyledInputAndLabel>
                <label htmlFor='day'>Day</label>
                <StyledSelect
                    value={props.day}
                    id={'day'}
                    onChange={
                        (e) => props.onDayChange(parseInt(e.target.value))}
                >
                    <option value={0}>All</option>
                    <option value={1}>1</option>
                    <option value={2}>2</option>
                    <option value={3}>3</option>
                    <option value={4}>4</option>
                    <option value={5}>5</option>
                    <option value={6}>6</option>
                    <option value={7}>7</option>
                    <option value={8}>8</option>
                    <option value={9}>9</option>
                    <option value={10}>10</option>
                    <option value={11}>11</option>
                    <option value={12}>12</option>
                    <option value={13}>13</option>
                    <option value={14}>14</option>
                    <option value={15}>15</option>
                    <option value={16}>16</option>
                    <option value={17}>17</option>
                    <option value={18}>18</option>
                    <option value={19}>19</option>
                    <option value={20}>20</option>
                    <option value={21}>21</option>
                    <option value={22}>22</option>
                    <option value={23}>23</option>
                    <option value={24}>24</option>
                    <option value={25}>25</option>
                    <option value={26}>26</option>
                    <option value={27}>27</option>
                    <option value={28}>28</option>
                    <option value={29}>29</option>
                    <option value={30}>30</option>
                    <option value={31}>31</option>
                </StyledSelect>
            </StyledInputAndLabel>
            <StyledInputAndLabel>
                <label htmlFor='term'>Term</label>
                <StyledSelect
                    value={!!props.term ? props.term : ''}
                    id={'term'}
                    onChange={
                        (e) => props.onTermChange(e.target.value)
                    }
                >
                    <option value={''}>All</option>
                    {props.terms.map((term) => <option value={term}>{term}</option>)}
                </StyledSelect>
            </StyledInputAndLabel>
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
    align-items: stretch;
    max-height: 100%;
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