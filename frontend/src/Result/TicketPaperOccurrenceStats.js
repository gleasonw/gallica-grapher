import React from "react";
import useData from "../shared/hooks/useData";
import styled from "styled-components";

export function TicketPaperOccurrenceStats(props) {
    const topPapersQuery =
        "/api/topPapers?ticket_ids=" + props.tickets +
        "&request_id=" + props.requestID +
        "&uuid=" + props.cacheID;

    const result = useData(topPapersQuery);
    if (result) {
        const topPapers = result['topPapers'];
        return (
            <StyledTopPaperTable>
                <tbody>
                <tr>
                    <th>Periodicals with the most occurrences</th>
                </tr>
                {topPapers.map((paperCount, index) => (
                    <tr key={paperCount[0]}>
                        <td>{index + 1}. {paperCount[0]}</td>
                        <td>{paperCount[1]}</td>
                    </tr>
                ))}
                </tbody>
            </StyledTopPaperTable>
        )
    } else {
        return null;
    }
}

const StyledTopPaperTable = styled.table`
    margin-top: 20px;
    margin-bottom: 30px;
    td {
        padding: 5px;
    }
    tr {
        border-bottom: 1px solid #ddd;
    }
`;

export default TicketPaperOccurrenceStats;