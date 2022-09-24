import React, {useContext, useState} from "react";
import DisplayRecordsTable from "./DisplayRecordsTable";
import Chart from "./Chart";
import DownloadCSVButton from "./DownloadCSVButton";
import {GraphSettingsContext} from "./GraphSettingsContext";
import ClassicUIBox from "../shared/ClassicUIBox";
import styled from "styled-components";
import {v4 as uuidv4} from 'uuid';

export default function RecordsViewer(props){
    const settings = useContext(GraphSettingsContext);
    const minYearsOfTickets = Object.keys(props.tickets).map(ticketID => {
        const ticket = props.tickets[ticketID];
        return ticket.dateRange[0]
    });
    const maxYearsOfTickets = Object.keys(props.tickets).map(ticketID => {
        const ticket = props.tickets[ticketID];
        return ticket.dateRange[1]
    });
    const minYear = Math.min(...minYearsOfTickets);
    const maxYear = Math.max(...maxYearsOfTickets);
    const middleYear = Math.floor((minYear + maxYear) / 2);
    const timeBin = settings[props.settingsID].timeBin;
    const [recordsTableYear, setRecordsTableYear] = useState(middleYear);
    const [recordsTableMonth, setRecordsTableMonth] = useState(null);
    const [recordsTableDay, setRecordsTableDay] = useState(null);
    const seriesClickHandlers = {
        'year': handleYearSeriesClick,
        'month': handleMonthSeriesClick,
        'day': handleDaySeriesClick
    }
    const uniqueIDToPreventCaching = uuidv4();

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
                    uuid={uniqueIDToPreventCaching}
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
                        onYearChange={setRecordsTableYear}
                        onMonthChange={setRecordsTableMonth}
                        onDayChange={setRecordsTableDay}
                        uuid={uniqueIDToPreventCaching}
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