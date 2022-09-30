import React from 'react';
import styled from "styled-components";
import ItemsBlurb from "./ItemsBlurb";

function TicketLabel(props) {
    return (
        <StyledTicketLabel compact={props.compact} center={props.center}>
            Occurrences of
            <ItemsBlurb terms={props.terms}/>
            {!!props.linkTerm && `when it appears within ${props.linkDistance} words of "${props.linkTerm}" `}
            in
            <ItemsBlurb papers={props.papers}/>
            from
            <ItemsBlurb dateRange={props.dateRange}/>
        </StyledTicketLabel>
    )
}

const StyledTicketLabel = styled.div`
    display: flex;
    font-size: ${props => props.compact ? '18px' : '25px'};
    flex-direction: ${props => props.compact ? 'column' : 'row'};
    flex-wrap: wrap;
    align-items: ${props => props.compact ? 'flex-start' : 'center'};
    gap: ${props => props.compact ? '5px' : '10px'};
    position: relative;
    overflow-y: ${props => props.compact ? 'auto' : 'hidden'};
    overflow-x: hidden;
    align-self: ${props => props.center ? 'center' : 'flex-start'};
`;


export default TicketLabel;
