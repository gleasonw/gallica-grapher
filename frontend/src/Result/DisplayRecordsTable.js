import React, {useState} from "react";
import useData from "../shared/hooks/useData";
import {StyledOccurrenceTable} from "../shared/StyledOccurrenceTable";
import NavBarWrap from "./NavBarWrap";
import styled from 'styled-components';
import OCRRecordDisplay from "./OCRRecordDisplay";

export default function DisplayRecordsTable(props){
    const [limit, setLimit] = useState(10);
    const [offset, setOffset] = useState(0);
    const recordsQuery =
        "/api/getDisplayRecords?" +
        "tickets=" + Object.keys(props.tickets) +
        "&requestID=" + props.requestID +
        "&year=" + props.year +
        "&month=" + props.month +
        "&day=" + props.day +
        "&limit=" + limit +
        "&offset=" + offset;
    const result = useData(recordsQuery);
    const displayRecords = result ? result['displayRecords'] : null;
    return (
        <div>
        <NavBarWrap>
            <StyledInputAndLabel>
                <label htmlFor='year'>Year</label>
                <input
                    type={'number'}
                    value={props.year}
                    id={'year'}
                    onChange={
                    (e) => props.onYearChange(parseInt(e.target.value))}
                    />
            </StyledInputAndLabel>
            <StyledInputAndLabel>
                <label htmlFor='month'>Month</label>
                <input
                    type={'number'}
                    value={props.month}
                    id={'month'}
                    onChange={
                    (e) => props.onMonthChange(parseInt(e.target.value))}
                    />
            </StyledInputAndLabel>
            <StyledInputAndLabel>
                <label htmlFor='day'>Day</label>
                <input
                    type={'number'}
                    value={props.day}
                    id={'day'}
                    onChange={
                    (e) => props.onDayChange(parseInt(e.target.value))}
                    />
            </StyledInputAndLabel>
            <StyledInputAndLabel>
                <label htmlFor='limit'>Limit</label>
                <input
                    type={'number'}
                    value={limit}
                    id={'limit'}
                    onChange={(e) => setLimit(parseInt(e.target.value))}
                    />
            </StyledInputAndLabel>
            <StyledInputAndLabel>
                <label htmlFor='offset'>Offset</label>
                <input
                    type={'number'}
                    value={offset}
                    id={'offset'}
                    onChange={(e) => setOffset(parseInt(e.target.value))}
                    />
            </StyledInputAndLabel>
        </NavBarWrap>
        <StyledOccurrenceTable>
            <tbody>
            <tr>
                <th></th>
                <th>Term</th>
                <th>Periodical</th>
                <th>Date</th>
                <th>Full text on Gallica</th>
                <th>OCR text</th>
            </tr>
            {displayRecords ?
                displayRecords.map((record, index) => (
                <tr key={index}>
                    <td>{index + offset + 1}</td>
                    <td>{record[0]}</td>
                    <td>{record[1]}</td>
                    <td>{record[2]}/{record[3]}/{record[4]}</td>
                    <td>
                        <a
                            href={record[5]}
                            target='_blank'
                            rel='noopener noreferrer'
                        >
                            {record[5]}</a>
                    </td>
                    <td>
                        <OCRRecordDisplay
                            identifier={record[5]}
                            term={record[0]}
                        />
                    </td>
                </tr>
            ))
                :
                <tr>
                    <td>Loading...</td>
                </tr>
            }
            </tbody>
        </StyledOccurrenceTable>
        </div>
    )
}

const StyledInputAndLabel = styled.div`
    display: flex;
    flex-direction: column;
    `;