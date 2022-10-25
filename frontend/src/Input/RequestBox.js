import React from "react";
import styled from 'styled-components';
import LesserButton from "../shared/LesserButton";
import AddBoxIcon from '@mui/icons-material/AddBox';
import TicketLabelRow from "./TicketLabelRow";

export function RequestBox(props) {
    return(
        <StyledTicketRow>
            <TicketLabelRow
                tickets={props.tickets}
                onTicketClick={props.onTicketClick}
                isMutable={true}
                maxWidth={'200px'}
            />
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

export const StyledTicketRow = styled.div`
    display: flex;
    flex-direction: row;
    overflow: visible;
    width: 100%;
`;

export const StyledRequestBox = styled(RequestBox)`
    display: flex;
    flex-direction: row;
    transition: all 150ms;
`;

