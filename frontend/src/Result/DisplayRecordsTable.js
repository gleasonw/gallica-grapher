import React, {useState} from "react";
import useData from "../shared/hooks/useData";
import {StyledOccurrenceTable} from "../shared/StyledOccurrenceTable";
import TicketPaperOccurrenceStats from "./TicketPaperOccurrenceStats";
import styled from 'styled-components';
import NavBarWrap from "./NavBarWrap";
import ImportantButtonWrap from "../shared/ImportantButtonWrap";
import LesserButton from "../shared/LesserButton";
import useWindowDimensions from "../shared/hooks/useWindowDimensions";
import {FilterOptions} from "./FilterOptions";
import {RecordRows} from "./RecordRows";
import {SelectionBubble} from "../shared/SelectionBubble";

export default function DisplayRecordsTable(props) {
    const [limit, setLimit] = useState(10);
    const [offset, setOffset] = useState(0);
    const [showFilterPopup, setShowFilterPopup] = useState(false);
    const {width} = useWindowDimensions();
    let compact = width < 1200;
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

    function handleFilterChange(){
        setOffset(0);
        setLimit(10);
    }

//TODO: use a reducer here to minimize prop drilling
    return (
        <StyledRecordsViewer>
            <NavBarWrap>
                <h2>
                    View {count}
                    {
                        [props.year, props.month, props.day, props.periodical, props.term].some(Boolean) ?
                            ' occurrences for these filters'
                            :
                            ' total occurrences'
                    }
                </h2>
                {
                    compact &&
                    <LesserButton
                        children={'Filter'}
                        onClick={() => setShowFilterPopup(true)}
                    />
                }
            </NavBarWrap>
            <StyledFilterAndTable
                onOutsidePopupClick={() => setShowFilterPopup(false)}
                compact={compact}
                show={showFilterPopup}
                year={props.year}
                month={props.month}
                day={props.day}
                periodical={props.periodical}
                term={props.term}
                limit={limit}
                offset={offset}
                setLimit={setLimit}
                setOffset={setOffset}
                onYearChange={(year) => handleFilterChange(
                    props.onYearChange(year)
                )}
                onMonthChange={(month) => handleFilterChange(
                    props.onMonthChange(month)
                )}
                onDayChange={(day) => handleFilterChange(
                    props.onDayChange(day)
                )}
                onPeriodicalChange={(periodical) => handleFilterChange(
                    props.onPeriodicalChange(periodical)
                )}
                onTermChange={(term) => handleFilterChange(
                    props.onTermChange(term)
                )}
                tickets={props.tickets}
                displayRecords={displayRecords}
                count={count}
                onLoadMoreClick={handleLoadMore}
                cacheID={props.cacheID}
                requestID={props.requestID}
            />

        </StyledRecordsViewer>
    )
}

function StyledFilterAndTable(props) {
    return (
        <StyledFilterAndTableWrap compact={props.compact}>
            <StyledFilterAndTopPapersWrap>
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
                    onOutsidePopupClick={props.onOutsidePopupClick}
                />
                <TicketPaperOccurrenceStats
                    tickets={Object.keys(props.tickets)}
                    requestID={props.requestID}
                    cacheID={props.cacheID}
                />
            </StyledFilterAndTopPapersWrap>
            <div>
                <AppliedFilters
                    year={props.year}
                    month={props.month}
                    day={props.day}
                    periodical={props.periodical}
                    term={props.term}
                    onYearClick={() => props.onYearChange(null)}
                    onMonthClick={() => props.onMonthChange(null)}
                    onDayClick={() => props.onDayChange(null)}
                    onPeriodicalClick={() => props.onPeriodicalChange(null)}
                    onTermClick={() => props.onTermChange(null)}
                />
                <StyledOccurrenceTable>
                    <tbody>
                    <tr>
                        <th>Date</th>
                        <th>Periodical</th>
                        <th>Term</th>
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
                                <td colSpan={6}>No records found for these options; clicking on a point in the graph
                                    should
                                    yield results.
                                </td>
                            </tr>
                        :
                        <tr>
                            <td>Loading...</td>
                        </tr>
                    }
                    </tbody>
                </StyledOccurrenceTable>
                {props.displayRecords && props.displayRecords.length !== props.count &&
                <ImportantButtonWrap
                    children={'Load more'}
                    onClick={props.onLoadMoreClick}
                />
                }
            </div>
        </StyledFilterAndTableWrap>
    )
}

//TODO: on click remove
function AppliedFilters(props) {
    const monthValues = {
        1: 'January',
        2: 'February',
        3: 'March',
        4: 'April',
        5: 'May',
        6: 'June',
        7: 'July',
        8: 'August',
        9: 'September',
        10: 'October',
        11: 'November',
        12: 'December'
    }
    return (
        <NavBarWrap>
            {!!props.year &&
                <SelectionBubble
                    onClick={props.onYearClick}
                >
                    {props.year}
                </SelectionBubble>
            }
            {!!props.month &&
                <SelectionBubble
                    item={monthValues[props.month]}
                    onClick={props.onMonthClick}
                >
                    {monthValues[props.month]}
                < /SelectionBubble>
            }
            {!!props.day &&
                <SelectionBubble
                    onClick={props.onDayClick}
                >
                    Day: {props.day}
                </SelectionBubble>
            }
            {!!props.periodical &&
                <SelectionBubble onClick={props.onPeriodicalClick}>
                    Periodical: {props.periodical}
                </SelectionBubble>
            }
            {!!props.term &&
                <SelectionBubble
                    onClick={props.onTermClick}
                >
                    {props.term}
                </SelectionBubble>
            }
        </NavBarWrap>
    )
}

const StyledFilterAndTableWrap = styled.div`
    display: flex;
    flex-direction: ${props => props.compact ? 'column' : 'row'};
    gap: 1em;
`;

const StyledFilterAndTopPapersWrap = styled.div`
    display: flex;
    flex-direction: column;
    gap: 1em;
    max-width: 20%;
`;

const StyledRecordsViewer = styled.div`
    display: flex;
    flex-direction: column;
    position: relative;
    `;



