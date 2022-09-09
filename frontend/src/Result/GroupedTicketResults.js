import React, {useContext} from "react";
import {GraphSettingsContext} from "./GraphSettingsContext";
import TicketLabel from "../shared/TicketLabel";
import Chart from "./Chart";
import TicketPaperOccurrenceStats from "./TicketPaperOccurrenceStats";
import DownloadCSVButton from "./DownloadCSVButton";
import ClassicUIBox from "../shared/ClassicUIBox";
import styled from "styled-components";

export function GroupedTicketResults(props) {
    return (
        <ClassicUIBox>
            <Chart
                tickets={props.tickets}
                settingsID='group'
            />
            <GroupedStatBar tickets={props.tickets}/>
            <DownloadCSVButton tickets={props.tickets}/>
        </ClassicUIBox>

    )
}

function GroupedStatBar(props) {
    const settings = useContext(GraphSettingsContext);


    return (
        <StyledStatBar>
            {Object.keys(props.tickets).map(key => (
                <div
                    className='groupedStatBarEntry'
                    key={key}
                >
                    <svg width = "20" height="20">
                        <circle cx="10" cy="10" r="10" fill={settings[key].color}/>
                    </svg>
                    <TicketLabel
                        terms={props.tickets[key].terms}
                        papers={props.tickets[key].papersAndCodes}
                        dateRange={props.tickets[key].dateRange}
                    />
                    <TicketPaperOccurrenceStats
                        ticketID={key}
                        dateRange={props.tickets[key].dateRange}
                        grouped={true}
                    />
                </div>
            ))}
        </StyledStatBar>
    );
}

const StyledStatBar = styled.div`
    display: flex;
    flex-direction: row;
`;

export default GroupedTicketResults;