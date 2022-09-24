import React, {useState} from "react";
import useData from "../shared/hooks/useData";
import {StyledOccurrenceTable} from "../shared/StyledOccurrenceTable";
import styled from 'styled-components';
import NavBarWrap from "./NavBarWrap";
import OCRTextBubble from "./OCRTextBubble";
import {ShadowedFocusInput} from "../shared/ShadowedFocusInput";
import {StyledInputAndLabel, StyledSelect} from "../shared/StyledSelect";

export default function DisplayRecordsTable(props) {
    const [limit, setLimit] = useState(10);
    const [offset, setOffset] = useState(0);
    let recordsQuery =
        "/api/getDisplayRecords?" +
        "tickets=" + Object.keys(props.tickets) +
        "&requestID=" + props.requestID +
        "&year=" + props.year +
        "&limit=" + limit +
        "&offset=" + offset +
        "&uniqueforcache=" + props.uuid;
    if (props.month) {
        (recordsQuery += "&month=" + props.month);
    }
    if (props.day) {
        recordsQuery += "&day=" + props.day
    }
    const result = useData(recordsQuery);
    const displayRecords = result ? result['displayRecords'] : null;
    return (
        <StyledRecordsViewer>
            <OptionsRow
                year={props.year}
                month={props.month}
                day={props.day}
                periodical={props.periodical}
                limit={limit}
                offset={offset}
                setLimit={setLimit}
                setOffset={setOffset}
                onYearChange={props.onYearChange}
                onMonthChange={props.onMonthChange}
                onDayChange={props.onDayChange}
                onPeriodicalChange={props.onPeriodicalChange}
            />
            <StyledOccurrenceTable>
                <tbody>
                <tr>
                    <th></th>
                    <th>Term</th>
                    <th>Periodical</th>
                    <th>Date</th>
                    <th>Full text image on Gallica</th>
                    <th>Scanned text (approximate)</th>
                </tr>
                {displayRecords ?
                    displayRecords.length > 0 ?
                        <RecordRows
                            rows={displayRecords}
                            offset={offset}
                        />
                        :
                        <tr>
                            <td colSpan={6}>No records found for these options; clicking on a point in the graph should
                                yield results.
                            </td>
                        </tr>
                    :
                    <tr>
                        <td>Loading...</td>
                    </tr>
                }
                </tbody>
            </StyledOccurrenceTable>
        </StyledRecordsViewer>
    )
}

function OptionsRow(props) {
    return (
        <NavBarWrap>
            <StyledInputAndLabel>
                <label htmlFor='year'>Year</label>
                <ShadowedFocusInput
                    type={'number'}
                    selected
                    value={props.year}
                    id={'year'}
                    onChange={
                        (e) => props.onYearChange(parseInt(e.target.value))}
                />
            </StyledInputAndLabel>
            <StyledInputAndLabel>
                <label htmlFor='month'>Month</label>
                <StyledSelect
                    value={props.month}
                    id={'month'}
                    onChange={
                        (e) => props.onMonthChange(parseInt(e.target.value))}
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
                <label htmlFor='limit'>Limit</label>
                <StyledSelect
                    value={props.limit}
                    id={'limit'}
                    onChange={(e) => props.setLimit(parseInt(e.target.value))}
                >
                    <option value={10}>10</option>
                    <option value={25}>25</option>
                    <option value={50}>50</option>
                    <option value={100}>100</option>
                </StyledSelect>
            </StyledInputAndLabel>
            <StyledInputAndLabel>
                <label htmlFor='offset'>Offset</label>
                <ShadowedFocusInput
                    type={'number'}
                    selected
                    value={props.offset}
                    id={'offset'}
                    onChange={(e) => props.setOffset(parseInt(e.target.value))}
                />
            </StyledInputAndLabel>
        </NavBarWrap>
    )
}

function RecordRows(props) {
    return (
        props.rows.map((record, index) => {
            let term = record[0];
            let periodical = record[1];
            let year = record[2];
            let month = record[3];
            let day = record[4];
            let gallicaLink = record[5];
            let arkCode = gallicaLink.split('/').pop();
            return (
                <tr key={index}>
                    <td>{index + props.offset + 1}</td>
                    <td>{term}</td>
                    <td>{periodical}</td>
                    <td>
                        {(year && month && day) && `${year}/${month}/${day}`}
                        {(year && month && !day) && `${year}/${month}`}
                        {(year && !month && !day) && `${year}`}
                    </td>
                    <td>
                        <a
                            href={gallicaLink}
                            target='_blank'
                            rel='noopener noreferrer'
                        >
                            {gallicaLink}</a>
                    </td>
                    <td>
                        <OCRTextBubble
                            term={term}
                            arkCode={arkCode}
                        />
                    </td>
                </tr>
            )
        })
    )
}

const StyledRecordsViewer = styled.div`
    display: flex;
    flex-direction: column;
    `;

