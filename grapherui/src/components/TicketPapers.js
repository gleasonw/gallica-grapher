import React, {useState, useEffect} from "react";
import Button from "@mui/material/Button";

export function TicketPapers(props) {
    const [topPapers, setTopPapers] = useState([]);

    useEffect(() => {
        let updatedPapers = [];
        console.log(props.ticketID)
        fetch(
            "/topPapers?id="+props.ticketID+
            "&continuous="+props.continuous+
            "&dateRange="+props.dateRange)
            .then(res => res.json())
            .then(result => {
                updatedPapers = result["topPapers"]
                setTopPapers(updatedPapers)
            })
    }, [props.continuous, props.dateRange, props.ticketID])

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