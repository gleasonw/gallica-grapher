import styled from "styled-components";
import Ticket from "./Ticket";
import SmallIconStyle from "../shared/SmallIconStyle";
import RemoveCircleIcon from "@mui/icons-material/RemoveCircle";
import React from "react";


export default function TicketLabelRow(props) {
    const numTickets = Object.keys(props.tickets).length
    const seriesColors = [
        '#7cb5ec',
        '#434348',
        '#90ed7d',
        '#f7a35c',
        '#8085e9'
    ]
    return (
        <StyledTicketLabelRow>
            {Object.keys(props.tickets).map((ticketID, index) => (
                <Ticket
                    ticket={props.tickets[ticketID]}
                    key={ticketID}
                    color={seriesColors[index]}
                    ticketID={ticketID}
                    firstInRow={index === 0}
                    lastInRow={index === numTickets - 1}
                    isMutable={props.isMutable}
                    maxWidth={props.maxWidth}
                    actionIcon={
                        props.isMutable ?
                        <SmallIconStyle onClick={() => props.onTicketClick(ticketID)}>
                            <RemoveCircleIcon/>
                        </SmallIconStyle>
                            :
                        null
                    }
                />
            ))}
        </StyledTicketLabelRow>
    )
}

export const StyledTicketLabelRow = styled.div`
    display: flex;
    flex-direction: row;
    overflow: visible;
    width: 100%;
    max-width: 100%;
`;