import {StyledInputAndLabel, StyledSelect} from "./StyledSelect";
import {ShadowedFocusInput} from "./ShadowedFocusInput";
import styled from "styled-components";

export function DateSelect(props) {
    return (
        <StyledDateSelect flexDirection={props.flexDirection}>
            <StyledInputAndLabel>
                <label htmlFor='year'>Year</label>
                <ShadowedFocusInput
                    type={'number'}
                    min={0}
                    selected
                    value={!!props.year ? props.year : ''}
                    id={'year'}
                    placeholder={'All'}
                    onChange={
                        (e) => props.onYearChange(e.target.value)
                    }
                    width={'86px'}
                />
            </StyledInputAndLabel>
            {
               !!props.month &&
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
            }
            {
                !!props.day &&
                <StyledInputAndLabel>
                    <label htmlFor='day'>Day</label>
                    <StyledSelect
                        value={!!props.day ? props.day : ''}
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
            }
        </StyledDateSelect>
    )
}

const StyledDateSelect = styled.div`
    display: flex;
    flex-direction: ${props => props.flexDirection ? props.flexDirection : 'column'}; 
    gap: 5px;
    flex-wrap: wrap;
    `;