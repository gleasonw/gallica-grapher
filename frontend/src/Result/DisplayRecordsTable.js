import React, {useState} from "react";
import useData from "../shared/hooks/useData";
import {StyledOccurrenceTable} from "../shared/StyledOccurrenceTable";
import styled from 'styled-components';
import NavBarWrap from "./NavBarWrap";
import ImportantButtonWrap from "../shared/ImportantButtonWrap";
import LesserButton from "../shared/LesserButton";
import useWindowDimensions from "../shared/hooks/useWindowDimensions";
import {FilterOptions} from "./FilterOptions";
import {RecordRows} from "./RecordRows";

export default function DisplayRecordsTable(props) {
    const [limit, setLimit] = useState(10);
    const [offset, setOffset] = useState(0);
    const [showFilterPopup, setShowFilterPopup] = useState(false);
    const {width} = useWindowDimensions();
    let compact = width < 1200;
    console.log(limit)
    let recordsQuery =
        "/api/getDisplayRecords?" +
        "tickets=" + Object.keys(props.tickets) +
        "&requestID=" + props.requestID +
        "&limit=" + limit +
        "&offset=" + offset +
        "&uniqueforcache=" + props.uuid;
    if (props.year) {
        recordsQuery += "&year=" + props.year;
    }
    if (props.month) {
        recordsQuery += "&month=" + props.month;
    }
    if (props.day) {
        recordsQuery += "&day=" + props.day
    }
    if (props.term) {
        recordsQuery += "&term=" + props.term
    }
    if (props.periodical) {
        recordsQuery += "&periodical=" + props.periodical
    }
    const result = useData(recordsQuery);
    const displayRecords = result ? result['displayRecords'] : null;
    const count = result ? result['count'] : null;

    function handleLoadMore() {
        console.log('load more')
        setLimit(limit + 10);
    }

//TODO: use a reducer here to minimize prop drilling
    return (
        <StyledRecordsViewer>
            <NavBarWrap>
                <h1>View {count} occurrences</h1>
                {
                    compact &&
                    <LesserButton
                        children={'Filter'}
                        onClick={() => setShowFilterPopup(!showFilterPopup)}
                    />
                }
            </NavBarWrap>
            <AppliedFilters
                year={props.year}
                month={props.month}
                day={props.day}
                periodical={props.periodical}
                term={props.term}
            />
            <StyledFilterAndTable
                compact={compact}
                show={showFilterPopup}
                year={props.year}
                month={props.month}
                day={props.day}
                periodical={props.periodical}
                limit={limit}
                offset={offset}
                setLimit={setLimit}
                setOffset={setOffset}
                onYearChange={props.onYearChange}
                onMonthChange={props.onMonthChange}
                onDayChange={props.onDayChange}
                onPeriodicalChange={props.onPeriodicalChange}
                onTermChange={props.onTermChange}
                tickets={props.tickets}
                displayRecords={displayRecords}
                count={count}
                onLoadMoreClick={handleLoadMore}
            />

        </StyledRecordsViewer>
    )
}

function StyledFilterAndTable(props) {
    return (
        <StyledFilterAndTableWrap compact={props.compact}>
            <FilterOptions
                year={props.year}
                month={props.month}
                day={props.day}
                periodical={props.periodical}
                limit={props.limit}
                offset={props.offset}
                setLimit={props.setLimit}
                setOffset={props.setOffset}
                onYearChange={props.onYearChange}
                onMonthChange={props.onMonthChange}
                onDayChange={props.onDayChange}
                onPeriodicalChange={props.onPeriodicalChange}
                onTermChange={props.onTermChange}
                terms={Object.keys(props.tickets).map((ticketID) => props.tickets[ticketID].terms)}
                count={props.count}
                compact={props.compact}
                show={props.show}
            />
            <StyledOccurrenceTable>
                <tbody>
                <tr>
                    <th></th>
                    <th>Term</th>
                    <th>Periodical</th>
                    <th>Date</th>
                    <th>Full text image on Gallica</th>
                    <th>Scanned text (approximate)</th>
                </tr>
                {props.displayRecords ?
                    props.displayRecords.length > 0 ?
                        <RecordRows
                            rows={props.displayRecords}
                            offset={props.offset}
                        />
                        :
                        <tr>
                            <td colSpan={6}>No records found for these options; clicking on a point in the graph should
                                yield results.
                            </td>
                        </tr>
                    :
                    <tr>
                        <td>Loading...</td>
                    </tr>
                }
                </tbody>
            <ImportantButtonWrap
                children={'Load more'}
                onClick={props.onLoadMoreClick}
            />
            </StyledOccurrenceTable>
        </StyledFilterAndTableWrap>
    )
}
//TODO: on click remove
function AppliedFilters(props){
    return(
        <NavBarWrap>
            {props.year && <p>Year: {props.year}</p>}
            {props.month && <p>Month: {props.month}</p>}
            {props.day && <p>Day: {props.day}</p>}
            {props.periodical && <p>Periodical: {props.periodical}</p>}
            {props.term && <p>Term: {props.term}</p>}
        </NavBarWrap>
    )
}

const StyledFilterAndTableWrap = styled.div`
    display: flex;
    flex-direction: ${props => props.compact ? 'column' : 'row'};
    gap: 1em;
`;

const StyledRecordsViewer = styled.div`
    display: flex;
    flex-direction: column;
    position: relative;
    `;



