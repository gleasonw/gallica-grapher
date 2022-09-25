import React, {useContext, useState} from "react";
import DisplayRecordsTable from "./DisplayRecordsTable";
import Chart from "./Chart";
import DownloadCSVButton from "./DownloadCSVButton";
import {GraphSettingsContext} from "./GraphSettingsContext";
import ClassicUIBox from "../shared/ClassicUIBox";
import styled from "styled-components";

export default function RecordsViewer(props){
    const settings = useContext(GraphSettingsContext);
    const timeBin = settings[props.settingsID].timeBin;
    const [recordsTableYear, setRecordsTableYear] = useState(null);
    const [recordsTableMonth, setRecordsTableMonth] = useState(null);
    const [recordsTableDay, setRecordsTableDay] = useState(null);
    const [recordsTableTerm, setRecordsTableTerm] = useState(null);
    const [recordsTablePeriodical, setRecordsTablePeriodical] = useState(null);
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
        <StyledRecordsViewer>
            <ClassicUIBox>
                <Chart
                    tickets={props.tickets}
                    settingsID={props.settingsID}
                    onSeriesClick={handleSeriesClick}
                    requestID={props.requestID}
                    uuid={props.cacheID}
                />
            </ClassicUIBox>
            <ClassicUIBox gap={'20px'}>
                <h4>View occurrences</h4>
                <DisplayRecordsTable
                        tickets={props.tickets}
                        requestID={props.requestID}
                        timeBin={props.timeBin}
                        year={recordsTableYear}
                        month={recordsTableMonth}
                        day={recordsTableDay}
                        term={recordsTableTerm}
                        periodical={recordsTablePeriodical}
                        onYearChange={setRecordsTableYear}
                        onMonthChange={setRecordsTableMonth}
                        onDayChange={setRecordsTableDay}
                        onPeriodicalChange={setRecordsTablePeriodical}
                        onTermChange={setRecordsTableTerm}
                        uuid={props.cacheID}
                    />
                <DownloadCSVButton
                    tickets={props.tickets}
                    requestID={props.requestID}
                />
            </ClassicUIBox>
        </StyledRecordsViewer>
    )
}

const StyledRecordsViewer = styled.div`
    display: flex;
    flex-direction: column;
    gap: 20px;
    margin-top: 20px;
    `;
