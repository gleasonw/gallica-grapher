import React from "react";
import useData from "./hooks/useData";
import {CSVDownload} from "react-csv";


function DownloadCSVButton(props) {
    const [downloadCSV, setDownloadCSV] = React.useState(false);

    function handleDownloadCSVclick() {
        setDownloadCSV(true);
    }

    function handleDownloadCSVclose() {
        setDownloadCSV(false);
    }

    return (
        <div>
            <input
                type={'button'}
                value={'Export all records (CSV)'}
                onClick={handleDownloadCSVclick}
            />
            {downloadCSV && <ExportCSV
                tickets={props.tickets}
                onClose={handleDownloadCSVclose}
            />}
        </div>
    );
}

function ExportCSV(props) {
    const ticketIDs = Object.keys(props.tickets);
    const query = "/api/getcsv?tickets=" + ticketIDs.join(",");
    const response = useData(query);

    if (response) {
        const csvData = response['csvData'];
        props.onClose();
        return <CSVDownload data={csvData} target="_blank"/>;
    } else {
        return 'Loading...';
    }
}

export default DownloadCSVButton;
