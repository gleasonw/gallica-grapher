import TicketLabel from "../shared/TicketLabel";
import React from "react";
import DecorativeTicket from "../shared/DecorativeTicket";
import styled from 'styled-components';
import LesserButton from "../shared/LesserButton";
import RemoveCircleIcon from '@mui/icons-material/RemoveCircle';
import SmallIconStyle from "../shared/SmallIconStyle";
import AddBoxIcon from '@mui/icons-material/AddBox';

export function RequestBox(props) {
    return(
        <StyledTicketRow>
            <OverflowScrollTicketRow>
                {Object.keys(props.tickets).map(ticketID => (
                    <DecorativeTicket key={ticketID}>
                        <SmallIconStyle onClick={() => props.onTicketClick(ticketID)}>
                            <RemoveCircleIcon/>
                        </SmallIconStyle>
                        <RequestTicket
                            ticket={props.tickets[ticketID]}
                        />
                    </DecorativeTicket>
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
`;

const OverflowScrollTicketRow = styled(StyledTicketRow)`
    overflow-x: scroll;
    overflow-y: visible;
`;

export const StyledRequestBox = styled(RequestBox)`
    display: flex;
    flex-direction: row;
    transition: all 150ms;
    overflow: visible;
`;

function RequestTicket(props) {
    const terms = props.ticket['terms']
    const papers = props.ticket['papersAndCodes']
    const dateRange = props.ticket['dateRange']
    return (
        <button
            type="button"
            onClick={props.onClick}
        >
            <div className="ticket">
                <TicketLabel
                    terms={terms}
                    papers={papers}
                    dateRange={dateRange}
                />
            </div>
        </button>
    );
}

