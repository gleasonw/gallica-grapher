import React from 'react';
import styled from "styled-components";
import {PaperBlurb} from "./ItemsBlurb";
import {DateBlurb} from "./ItemsBlurb";
import {TermsBlurb} from "./ItemsBlurb";

function TicketLabel(props) {
    const dateRange = [props.startDate, props.endDate]
    return (
        <StyledTicketLabel compact={props.compact} center={props.center}>
            Occurrences of
            <TermsBlurb terms={props.terms}/>
            {!!props.linkTerm &&
                `within ${props.linkDistance} words of "${props.linkTerm}" `
            }
            in
            <PaperBlurb papers={props.papers}/>
            {
                dateRange.length > 0 &&
                <StyledDateLine> between <DateBlurb dateRange={dateRange}/></StyledDateLine>
            }
        </StyledTicketLabel>
    )
}

const StyledTicketLabel = styled.div`
    display: flex;
    font-size: ${props => props.compact ? '18px' : '25px'};
    flex-direction: ${props => props.compact ? 'column' : 'row'};
    flex-wrap: wrap;
    max-width: 100%;
    align-items: ${props => props.compact ? 'flex-start' : 'center'};
    gap: ${props => props.compact ? '5px' : '10px'};
    position: relative;
    overflow-y: ${props => props.compact ? 'auto' : 'hidden'};
    align-self: ${props => props.center ? 'center' : 'flex-start'};
`;

const StyledDateLine = styled.div`
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    gap: 10px;
    align-items: center;
`;


export default TicketLabel;
