import React, {useContext} from "react";
import {GraphSettingsContext} from "./GraphSettingsContext";
import useData from "../shared/hooks/useData";
import {StyledOccurrenceTable} from "../shared/StyledOccurrenceTable";

export function TicketPaperOccurrenceStats(props) {
    const settings = useContext(GraphSettingsContext);
    const ticketSettings = props.grouped ? settings.group : settings[props.ticketID];
    const topPapersQuery =
        "/api/topPapers?ticketID="+props.ticketID+
        "&requestID="+props.requestID +
        "&continuous="+ticketSettings.continuous+
        "&dateRange="+props.dateRange +
        "&uuid="+props.uuid;

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

export default TicketPaperOccurrenceStats;