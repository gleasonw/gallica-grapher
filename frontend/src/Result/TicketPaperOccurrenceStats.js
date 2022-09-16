import React from "react";
import {useContext} from "react";
import {GraphSettingsContext} from "./GraphSettingsContext";
import useData from "../shared/hooks/useData";
import styled from "styled-components";

export function TicketPaperOccurrenceStats(props) {
    const settings = useContext(GraphSettingsContext);
    const ticketSettings = props.grouped ? settings.group : settings[props.ticketID];
    const query =
        "/api/topPapers?id="+props.ticketID+
        "&continuous="+ticketSettings.continuous+
        "&dateRange="+props.dateRange

    const result = useData(query);
    if(result){
        const topPapers = result['topPapers'];
        return (
            <div className='ticketStats'>
                <StyledOccurrenceTable>
                    <tbody>
                        <tr>
                            <th>Paper</th>
                            <th>Total Occurrences</th>
                        </tr>
                        {topPapers.map(paperCount => (
                            <tr key={paperCount[0]}>
                                <td>{paperCount[0]}</td>
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
    max-width: 600px;
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
`;

export default TicketPaperOccurrenceStats;