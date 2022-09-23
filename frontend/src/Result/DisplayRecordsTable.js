import React, {useState} from "react";
import useData from "../shared/hooks/useData";
import {StyledOccurrenceTable} from "../shared/StyledOccurrenceTable";
import styled from 'styled-components';
import OCRTextBubble from "./OCRTextBubble";
import {ShadowedFocusInput} from "../shared/ShadowedFocusInput";

export default function DisplayRecordsTable(props) {
    const [limit, setLimit] = useState(10);
    const [offset, setOffset] = useState(0);
    let recordsQuery =
        "/api/getDisplayRecords?" +
        "tickets=" + Object.keys(props.tickets) +
        "&requestID=" + props.requestID +
        "&year=" + props.year +
        "&limit=" + limit +
        "&offset=" + offset;
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
        <StyledOptions>
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
                <ShadowedFocusInput
                    type={'number'}
                    selected
                    value={props.month}
                    id={'month'}
                    onChange={
                        (e) => props.onMonthChange(parseInt(e.target.value))}
                />
            </StyledInputAndLabel>
            <StyledInputAndLabel>
                <label htmlFor='day'>Day</label>
                <ShadowedFocusInput
                    type={'number'}
                    selected
                    value={props.day}
                    id={'day'}
                    onChange={
                        (e) => props.onDayChange(parseInt(e.target.value))}
                />
            </StyledInputAndLabel>
            <StyledInputAndLabel>
                <label htmlFor='periodical'>Periodical</label>
                <ShadowedFocusInput
                    type={'text'}
                    selected
                    value={props.periodical}
                    id={'day'}
                    onChange={
                        (e) => props.onPeriodicalChange(e.target.value)}
                />
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
        </StyledOptions>
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

const StyledInputAndLabel = styled.div`
    display: flex;
    flex-direction: column;
    `;

const StyledOptions = styled.div`
    display: flex;
    flex-direction: column;
    `;

const StyledRecordsViewer = styled.div`
    display: flex;
    flex-direction: row;
    change flex-direction to column when under 600px
    @media screen and (max-width: 600px) {
        flex-direction: column;
    }
    `;

const StyledSelect = styled.select`
    padding: 5px;
    outline: none;
    background-color: inherit;
    box-shadow: rgba(0, 0, 0, 0.075) 0px 1px 1px 0px inset;
    cursor: pointer;
    border: 0.2rem solid #ece9e2;
    border-radius: 5px;
    `;