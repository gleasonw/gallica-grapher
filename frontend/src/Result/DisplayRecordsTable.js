import React, {useState} from "react";
import useData from "../shared/hooks/useData";
import {StyledOccurrenceTable} from "../shared/StyledOccurrenceTable";
import NavBarWrap from "./NavBarWrap";
import styled from 'styled-components';
import OCRTextBubble from "./OCRTextBubble";

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
    if(props.month) {
        (recordsQuery += "&month=" + props.month);
    }
    if(props.day) {
        recordsQuery += "&day=" + props.day
    }
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
                    <th>Full text image on Gallica</th>
                    <th>Scanned text (approximate)</th>
                </tr>
                {displayRecords ?
                    displayRecords.map((record, index) => {
                        let term = record[0];
                        let periodical = record[1];
                        let year = record[2];
                        let month = record[3];
                        let day = record[4];
                        let gallicaLink = record[5];
                        let arkCode = gallicaLink.split('/').pop();
                        return (
                            <tr key={index}>
                                <td>{index + offset + 1}</td>
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