import React, {useContext, useState} from "react";
import {GraphSettingsContext} from "./GraphSettingsContext";
import TicketLabel from "../shared/TicketLabel";
import Chart from "./Chart";
import TicketPaperOccurrenceStats from "./TicketPaperOccurrenceStats";
import DownloadCSVButton from "./DownloadCSVButton";
import ClassicUIBox from "../shared/ClassicUIBox";
import styled from "styled-components";
import DecorativeTicket from "../shared/DecorativeTicket";
import SeriesColorBubble from "../shared/SeriesColorBubble";
import DisplayRecordsTable from "./DisplayRecordsTable";

export function GroupedTicketResults(props) {
    const settings = useContext(GraphSettingsContext);
    const timeBin = settings.group.timeBin;
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
        <ClassicUIBox>
            <Chart
                tickets={props.tickets}
                settingsID='group'
                onSeriesClick={handleSeriesClick}
            />
            <StyledStatBar>
                <DisplayRecordsTable
                    tickets={props.tickets}
                    requestID={props.requestID}
                    timeBin={timeBin}
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
            </StyledStatBar>
            <GroupedStatBar
                tickets={props.tickets}
                requestID={props.requestID}
            />
        </ClassicUIBox>

    )
}

function GroupedStatBar(props) {
    const settings = useContext(GraphSettingsContext);


    return (
        <StyledStatBar>
            {Object.keys(props.tickets).map(key => (
                <DecorativeTicket
                    key={key}
                    height={'100%'}
                >
                    <SeriesColorBubble color={settings[key].color}/>
                    <TicketLabel
                        terms={props.tickets[key].terms}
                        papers={props.tickets[key].papersAndCodes}
                        dateRange={props.tickets[key].dateRange}
                    />
                    <TicketPaperOccurrenceStats
                        ticketID={key}
                        dateRange={props.tickets[key].dateRange}
                        grouped={true}
                        requestID={props.requestID}
                    />
                </DecorativeTicket>
            ))}
        </StyledStatBar>
    );
}

const StyledStatBar = styled.div`
    margin-top: 10px;
    margin-bottom: 10px;
    display: flex;
    flex-direction: column;
    gap: 10px;
`;

export default GroupedTicketResults;