import React from 'react';
import styled from "styled-components";
import ItemsBlurb from "./ItemsBlurb";
import {StyledTicketLabel} from "./StyledTicketLabel";

function TicketLabel(props){
    if(props.compact){
        return(
            <StyledCompactTicketLabel>
                Occurrences of
                <ItemsBlurb terms={props.terms}/>
                in
                <ItemsBlurb papers={props.papers}/>
                from
                <ItemsBlurb dateRange={props.dateRange}/>
            </StyledCompactTicketLabel>
        )
    }else{
        return(
            <StyledTicketLabel>
                Occurrences
                <span>of</span>
                <ItemsBlurb terms={props.terms}/>
                in
                <ItemsBlurb papers={props.papers}/>
                from
                <ItemsBlurb dateRange={props.dateRange}/>
            </StyledTicketLabel>
        )
    }
}

const StyledCompactTicketLabel = styled.div`
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
`;


export default TicketLabel;
