import React from "react";
import {useContext} from "react";
import {GraphSettingsContext} from "./GraphSettingsContext";
import useData from "./hooks/useData";

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
                <table className='topPaperTable'>
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
                </table>
            </div>
        )
    }else{
        return null;
    }
}

export default TicketPaperOccurrenceStats;