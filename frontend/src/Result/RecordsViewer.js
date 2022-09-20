import React, {useContext, useState} from "react";
import DisplayRecordsTable from "./DisplayRecordsTable";
import Chart from "./Chart";
import DownloadCSVButton from "./DownloadCSVButton";
import {GraphSettingsContext} from "./GraphSettingsContext";

export default function RecordsViewer(props){
    const settings = useContext(GraphSettingsContext);
    const timeBin = settings[props.ticketID || 'group'].timeBin;
    const [recordsTableYear, setRecordsTableYear] = useState(1905);
    const [recordsTableMonth, setRecordsTableMonth] = useState(0);
    const [recordsTableDay, setRecordsTableDay] = useState(0);
    const seriesClickHandlers = {
        'year': handleYearSeriesClick,
        'month': handleMonthSeriesClick,
        'day': handleDaySeriesClick
    }

    function handleSeriesClick(point){
        seriesClickHandlers[timeBin](point.category);
    }

    function handleYearSeriesClick(year){
        setRecordsTableYear(year);
        setRecordsTableMonth(0);
        setRecordsTableDay(0);
    }

    function handleMonthSeriesClick(unix){
        const date = new Date(unix);
        setRecordsTableYear(date.getUTCFullYear());
        setRecordsTableMonth(date.getUTCMonth() + 1);
        setRecordsTableDay(0);
    }

    //TODO: fix the date offset
    function handleDaySeriesClick(unix){
        // const date = new Date(unix);
        // console.log(date.getDay())
        // setRecordsTableYear(date.getFullYear());
        // setRecordsTableMonth(date.getUTCMonth() + 1);
        // setRecordsTableDay(date.getUTCDay());
    }

    return (
        <div>
            <Chart
                tickets={props.tickets}
                settingsID='group'
                onSeriesClick={handleSeriesClick}
            />
            <DisplayRecordsTable
                    tickets={props.tickets}
                    requestID={props.requestID}
                    timeBin={props.timeBin}
                    year={recordsTableYear}
                    month={recordsTableMonth}
                    day={recordsTableDay}
                    onYearChange={setRecordsTableYear}
                    onMonthChange={setRecordsTableMonth}
                    onDayChange={setRecordsTableDay}
                />
            <DownloadCSVButton
                tickets={props.tickets}
                requestID={props.requestID}
            />
        </div>
    )
}