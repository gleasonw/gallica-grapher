import React from "react";
import useData from "../shared/hooks/useData";
import {CSVDownload} from "react-csv";
import LesserButton from "../shared/LesserButton";


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
            <LesserButton
                type={'button'}
                onClick={handleDownloadCSVclick}
            >
                Export all records (CSV)
            </LesserButton>
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
        return <CSVDownload
            data={csvData}
            target="_blank"
            filename='allRecordsExport.csv'
        />;
    } else {
        return 'Loading...';
    }
}

export default DownloadCSVButton;
