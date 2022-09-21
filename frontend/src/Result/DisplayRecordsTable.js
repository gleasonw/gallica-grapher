import React, {useState} from "react";
import useData from "../shared/hooks/useData";
import {StyledOccurrenceTable} from "../shared/StyledOccurrenceTable";
import NavBarWrap from "./NavBarWrap";
import styled from 'styled-components';

export default function DisplayRecordsTable(props) {
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
    console.log(result);
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
                    <th>Number of hits</th>
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
                        let numHitsInPeriodical = record[6];
                        let ocrInfo = record[7];
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
                                <td>{numHitsInPeriodical}</td>
                                <td>
                                    {ocrInfo.map((info) => {
                                        let pageNumberText = info[0];
                                        let pageNumber = pageNumberText.split('_').pop();
                                        let ocrText = info[1];
                                        let htmlPageLink =`https://gallica.bnf.fr/ark:/12148/${arkCode}.f${pageNumber}.item.texteBrut`
                                        return (
                                            <div key={pageNumberText}>
                                                <a
                                                    href={htmlPageLink}
                                                    target='_blank'
                                                    rel='noopener noreferrer'
                                                >
                                                    {pageNumberText}
                                                </a>
                                                <div dangerouslySetInnerHTML={{__html: ocrText}}/>
                                            </div>
                                            )
                                    })}
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