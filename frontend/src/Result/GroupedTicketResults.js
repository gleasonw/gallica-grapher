import React, {useContext} from "react";
import {GraphSettingsContext} from "./GraphSettingsContext";
import TicketLabel from "../shared/TicketLabel";
import Chart from "./Chart";
import TicketPaperOccurrenceStats from "./TicketPaperOccurrenceStats";
import DownloadCSVButton from "./DownloadCSVButton";
import ClassicUIBox from "../shared/ClassicUIBox";
import styled from "styled-components";
import DecorativeTicket from "../shared/DecorativeTicket";
import SeriesColorBubble from "../shared/SeriesColorBubble";

export function GroupedTicketResults(props) {
    return (
        <ClassicUIBox>
            <Chart
                tickets={props.tickets}
                settingsID='group'
            />
            <GroupedStatBar
                tickets={props.tickets}
                requestID={props.requestID}
            />
            <DownloadCSVButton
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
    flex-direction: row;
    flex-wrap: wrap;
    gap: 10px;
    align-items: flex-start;
`;

export default GroupedTicketResults;