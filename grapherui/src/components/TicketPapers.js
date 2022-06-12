import React, {useState, useEffect} from "react";
import Button from "@mui/material/Button";
import {useContext} from "@types/react";
import {GraphSettingsContext} from "./GraphSettingsContext";

export function TicketPapers(props) {
    const [topPapers, setTopPapers] = useState([]);
    const settings = useContext(GraphSettingsContext);
    const ticketSettings = settings[props.ticketID];
    useEffect(() => {
        let updatedPapers = [];
        fetch(
            "/topPapers?id="+props.ticketID+
            "&continuous="+ticketSettings.continuous+
            "&dateRange="+ticketSettings.dateRange)
            .then(res => res.json())
            .then(result => {
                updatedPapers = result["topPapers"]
                setTopPapers(updatedPapers)
            })
    }, [props.ticketID, ticketSettings.continuous, ticketSettings.dateRange])

    return (
        <div className='ticketStats'>
            <table className='topPaperTable'>
                <tr>
                    <th>Paper</th>
                    <th>Count</th>
                </tr>
                {topPapers.map(paperCount => (
                    <tr>
                        <td>{paperCount[0]}</td>
                        <td>{paperCount[1]}</td>
                    </tr>
                ))}
            </table>
            <Button variant='text'>
                Download full result CSV
            </Button>
        </div>
    )
}

export default TicketPapers;