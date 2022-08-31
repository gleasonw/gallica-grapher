import React from "react";
import useData from "./hooks/useData";
import {CSVDownload} from "react-csv";


function DownloadCSVButton(props) {
    const [downloadCSV, setDownloadCSV] = React.useState(false);

    function handleDownloadCSVclick() {
        setDownloadCSV(true);
    }

    return (
        <div>
            <input
                type={'button'}
                value={'Download CSV'}
                onClick={handleDownloadCSVclick}
            />
            {downloadCSV && <ExportCSV tickets={props.tickets}/>}
        </div>
    );
}

function ExportCSV(props) {
    const ticketIDs = Object.keys(props.tickets);
    const query = "/api/getcsv?tickets=" + ticketIDs.join(",");
    const response = useData(query);

    if (response) {
        const csvData = response['csvData'];
        return <CSVDownload data={csvData} target="_blank"/>;
    } else {
        return 'Loading...';
    }
}

export default DownloadCSVButton;
