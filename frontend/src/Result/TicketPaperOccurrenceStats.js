import React from "react";
import {useContext} from "react";
import {GraphSettingsContext} from "./GraphSettingsContext";
import useData from "../shared/hooks/useData";
import styled from "styled-components";

export function TicketPaperOccurrenceStats(props) {
    const settings = useContext(GraphSettingsContext);
    const ticketSettings = props.grouped ? settings.group : settings[props.ticketID];
    const topPapersQuery =
        "/api/topPapers?ticketID="+props.ticketID+
        "&requestID="+props.requestID +
        "&continuous="+ticketSettings.continuous+
        "&dateRange="+props.dateRange
    const result = useData(topPapersQuery);
    if(result){
        const topPapers = result['topPapers'];
        return (
            <div className='ticketStats'>
                <StyledOccurrenceTable>
                    <tbody>
                        <tr>
                            <th>Papers with the most occurrences</th>
                            <th>Total Occurrences</th>
                        </tr>
                        {topPapers.map((paperCount, index) => (
                            <tr key={paperCount[0]}>
                                <td><h5>{index+1}.</h5> {paperCount[0]}</td>
                                <td>{paperCount[1]}</td>
                            </tr>
                        ))}
                    </tbody>
                </StyledOccurrenceTable>
            </div>
        )
    }else{
        return null;
    }
}

const StyledOccurrenceTable = styled.table`
    border-collapse: collapse;
    table-layout: fixed;
    td{
        padding: 5px;
    }
    td:hover{
        overflow: visible;
        white-space: normal;
        height: auto;
    }
    tr:nth-child(even){
        background-color: #f2f2f2;
    }
    min-width: 100%;
`;

export default TicketPaperOccurrenceStats;