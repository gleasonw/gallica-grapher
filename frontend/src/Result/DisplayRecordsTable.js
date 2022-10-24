import React, {useState} from "react";
import useData from "../shared/hooks/useData";
import {StyledOccurrenceTable} from "../shared/StyledOccurrenceTable";
import TicketPaperOccurrenceStats from "./TicketPaperOccurrenceStats";
import styled from 'styled-components';
import NavBarWrap from "./NavBarWrap";
import ImportantButtonWrap from "../shared/ImportantButtonWrap";
import LesserButton from "../shared/LesserButton";
import {FilterOptions} from "./FilterOptions";
import {RecordRows} from "./RecordRows";
import {SelectionBubble} from "../shared/SelectionBubble";
import DownloadCSVButton from "./DownloadCSVButton";

export default function DisplayRecordsTable(props) {
    const [limit, setLimit] = useState(Math.round(10 / Object.keys(props.tickets).length));
    const [offset, setOffset] = useState(0);
    const [showFilterPopup, setShowFilterPopup] = useState(false);
    const isGallicaGrouped = props.timeBin === 'gallicaYear' || props.timeBin === 'gallicaMonth';
    const ticketToDisplay = props.selectedTicket ? {[props.selectedTicket]: props.tickets[props.selectedTicket]} : props.tickets;
    const result = useData(isGallicaGrouped ?
        buildGallicaQuery(ticketToDisplay) :
        buildDBQuery(ticketToDisplay)
    );
    const displayRecords = result ? result['displayRecords'] : null;
    const count = result ? result['count'] : null;

    function handleFilterChange() {
        setOffset(0);
        setLimit(10);
    }

    function buildDBQuery(tickets){
        let query =
            "/api/getDisplayRecords?" +
            "tickets=" + Object.keys(tickets) +
            "&requestID=" + props.requestID +
            "&limit=" + limit +
            "&offset=" + offset +
            "&uniqueforcache=" + props.cacheID;
        return addFiltersToQuery(query);
    }

    function buildGallicaQuery(tickets){
        let argsForQuery = Object.keys(tickets).map((key) => {
            const ticket = tickets[key];
            return {
                terms: ticket.terms,
                linkTerm: ticket.linkTerm,
                linkDistance: ticket.linkDistance,
                grouping: 'all',
                startDate: buildDateStringForFilters() || ticket.startDate,
            }
        });
        argsForQuery = JSON.stringify(argsForQuery);
        return "/api/getGallicaRecords?" +
            "tickets=" + argsForQuery +
            "&limit=" + limit +
            "&offset=" + offset;
    }

    function buildDateStringForFilters(){
        if(props.year && props.month && props.day){
            return `${props.year}-${props.month}-${props.day}`
        }else if(props.year && props.month){
            return `${props.year}-${props.month}`
        }else if(props.year){
            return `${props.year}`
        }else{
            return null
        }
    }


    function addFiltersToQuery(query){
        if (props.year) {
            query += "&year=" + props.year;
        }
        if (props.month) {
            query += "&month=" + props.month;
        }
        if (props.day) {
            query += "&day=" + props.day
        }
        if (props.periodical) {
            query += "&periodical=" + props.periodical
        }
        return query;
    }

//TODO: use a reducer here to minimize prop drilling
    return (
        <StyledRecordsViewer>
            <NavBarWrap>
                <h3>
                    View {count}
                    {
                        [props.year, props.month, props.day, props.periodical, props.ticket].some(Boolean) ?
                            ' occurrences for these filters'
                            :
                            ' total occurrences'
                    }
                </h3>
                {
                    props.compact &&
                    <LesserButton
                        children={'Filter'}
                        onClick={() => setShowFilterPopup(true)}
                    />
                }
            </NavBarWrap>
            <StyledFilterAndTable
                isGallicaGrouped={isGallicaGrouped}
                onOutsidePopupClick={() => setShowFilterPopup(false)}
                compact={props.compact}
                show={showFilterPopup}
                year={props.year}
                month={props.month}
                day={props.day}
                periodical={props.periodical}
                selectedTicket={props.selectedTicket}
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
                onSelectedTicketChange={(ticket) => handleFilterChange(
                    props.onSelectedTicketChange(ticket)
                )}
                tickets={props.tickets}
                displayRecords={displayRecords}
                count={count}
                onLoadMoreClick={() => setLimit(limit + 10)}
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
                    selectedTicket={props.selectedTicket}
                    limit={props.limit}
                    offset={props.offset}
                    setLimit={props.setLimit}
                    setOffset={props.setOffset}
                    onYearChange={props.onYearChange}
                    onMonthChange={props.onMonthChange}
                    onDayChange={props.onDayChange}
                    onPeriodicalChange={props.onPeriodicalChange}
                    onSelectedTicketChange={props.onSelectedTicketChange}
                    tickets={props.tickets}
                    count={props.count}
                    compact={props.compact}
                    show={props.show}
                    onOutsidePopupClick={props.onOutsidePopupClick}
                />
                {!props.compact && !props.isGallicaGrouped &&
                    <div>
                        <TicketPaperOccurrenceStats
                            tickets={Object.keys(props.tickets)}
                            requestID={props.requestID}
                            cacheID={props.cacheID}
                        />
                        <DownloadCSVButton
                            tickets={props.tickets}
                            requestID={props.requestID}
                        />
                    </div>
                }
            </StyledFilterAndTopPapersWrap>
            <StyledAppliedFiltersTableWrap>
                <AppliedFilters
                    year={props.year}
                    month={props.month}
                    day={props.day}
                    periodical={props.periodical}
                    selectedTicket={props.selectedTicket}
                    tickets={props.tickets}
                    onYearClick={() => props.onYearChange(null)}
                    onMonthClick={() => props.onMonthChange(null)}
                    onDayClick={() => props.onDayChange(null)}
                    onPeriodicalClick={() => props.onPeriodicalChange(null)}
                    onTicketClick={() => props.onSelectedTicketChange(null)}
                />
                <StyledOccurrenceTable>
                    <tbody>
                    <tr>
                        <th>Date</th>
                        {!props.compact && <th>Periodical</th>}
                        <th>Term</th>
                        <th>Scanned context (approximate)</th>
                        {!props.compact && <th>Full text image on Gallica</th>}
                    </tr>
                    {props.displayRecords ?
                        props.displayRecords.length > 0 ?
                            <RecordRows
                                rows={props.displayRecords}
                                offset={props.offset}
                                compact={props.compact}
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
            </StyledAppliedFiltersTableWrap>
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
            {!!props.selectedTicket &&
                <SelectionBubble
                    onClick={props.onTicketClick}
                >
                    {Number(props.selectedTicket) + 1}: {props.tickets[props.selectedTicket].terms}
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

const StyledAppliedFiltersTableWrap = styled.div`
    display: flex;
    flex-direction: column;
    width: 100%;
`;



