import React, {useContext, useState} from "react";
import DisplayRecordsTable from "./DisplayRecordsTable";
import Chart from "./Chart";
import {GraphSettingsContext} from "./GraphSettingsContext";
import ClassicUIBox from "../shared/ClassicUIBox";
import styled from "styled-components";
import useWindowDimensions from "../shared/hooks/useWindowDimensions";

export default function RecordsViewer(props){
    const settings = useContext(GraphSettingsContext);
    const timeBin = settings[props.settingsID].timeBin;
    const [recordsTableYear, setRecordsTableYear] = useState(null);
    const [recordsTableMonth, setRecordsTableMonth] = useState(null);
    const [recordsTableDay, setRecordsTableDay] = useState(null);
    const [recordsTableTicket, setRecordsTableTicket] = useState(null);
    const [recordsTablePeriodical, setRecordsTablePeriodical] = useState(null);
    const {width} = useWindowDimensions();
    let compact = width < 800;
    const seriesClickHandlers = {
        'year': handleYearSeriesClick,
        'month': handleMonthSeriesClick,
        'day': handleDaySeriesClick,
        'gallicaYear': handleYearSeriesClick,
        'gallicaMonth': handleMonthSeriesClick,
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
        const date = new Date(unix);
        setRecordsTableYear(date.getUTCFullYear());
        setRecordsTableMonth(date.getUTCMonth() + 1);
        setRecordsTableDay(date.getUTCDate());
    }

    return (
        <StyledRecordsViewer>
            <ClassicUIBox padding={compact ? '0' : '20px'}>
                <Chart
                    tickets={props.tickets}
                    settingsID={props.settingsID}
                    onSeriesClick={(point) => seriesClickHandlers[timeBin](point.category)}
                    requestID={props.requestID}
                    uuid={props.cacheID}
                />
            </ClassicUIBox>
            <ClassicUIBox gap={'20px'}>
                <DisplayRecordsTable
                    tickets={props.tickets}
                    requestID={props.requestID}
                    timeBin={timeBin}
                    year={recordsTableYear}
                    month={recordsTableMonth}
                    day={recordsTableDay}
                    selectedTicket={recordsTableTicket}
                    periodical={recordsTablePeriodical}
                    onYearChange={setRecordsTableYear}
                    onMonthChange={setRecordsTableMonth}
                    onDayChange={setRecordsTableDay}
                    onPeriodicalChange={setRecordsTablePeriodical}
                    onSelectedTicketChange={setRecordsTableTicket}
                    cacheID={props.cacheID}
                    compact={compact}
                />
            </ClassicUIBox>
        </StyledRecordsViewer>
    )
}

const StyledRecordsViewer = styled.div`
    display: flex;
    flex-direction: column;
    flex-wrap: wrap;
    gap: 20px;
    margin-top: 20px;
    `;
