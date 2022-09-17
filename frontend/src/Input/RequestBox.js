import React from "react";
import styled from 'styled-components';
import LesserButton from "../shared/LesserButton";
import AddBoxIcon from '@mui/icons-material/AddBox';
import Ticket from "./Ticket";
import SmallIconStyle from "../shared/SmallIconStyle";
import RemoveCircleIcon from "@mui/icons-material/RemoveCircle";

export function RequestBox(props) {
    const numTickets = Object.keys(props.tickets).length
    const seriesColors = [
        '#7cb5ec',
        '#434348',
        '#90ed7d',
        '#f7a35c',
        '#8085e9'
    ]
    return(
        <StyledTicketRow>
            <OverflowScrollTicketRow>
                {Object.keys(props.tickets).map((ticketID,index) => (
                    <Ticket
                        ticket={props.tickets[ticketID]}
                        key={ticketID}
                        color={seriesColors[index]}
                        ticketID={ticketID}
                        firstInRow = {index === 0}
                        lastInRow = {index === numTickets - 1}
                        actionIcon={
                            <SmallIconStyle onClick={() => props.onTicketClick(ticketID)}>
                                <RemoveCircleIcon/>
                            </SmallIconStyle>
                        }
                    />
                ))}
            </OverflowScrollTicketRow>
            {Object.keys(props.tickets).length < 5 &&
            <LesserButton
                onClick={props.onCreateTicketClick}
                borderRadius="0px 0px 10px 10px"
            >
                <AddBoxIcon/>
                Compare
            </LesserButton>
            }
        </StyledTicketRow>
    )
}

const StyledTicketRow = styled.div`
    display: flex;
    flex-direction: row;
    overflow: visible;
    width: 100%;
`;

const OverflowScrollTicketRow = styled(StyledTicketRow)`
    max-width: 100%;
`;

export const StyledRequestBox = styled(RequestBox)`
    display: flex;
    flex-direction: row;
    transition: all 150ms;
`;

