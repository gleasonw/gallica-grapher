import styled from "styled-components";

export const BlurbText = styled.section`
    max-width: ${props => props.expanded ? '100%' : '150px'};
    max-height: 180px;
    overflow: ${props => props.expanded ? 'visible' : 'hidden'};
    position: ${props => props.expanded ? 'absolute' : 'relative'};
    text-overflow: ellipsis;
    white-space: ${props => props.expanded ? 'wrap' : 'nowrap'};
    z-index: ${props => props.expanded ? '1' : '0'};
    padding: 10px;
    border-radius: 3px;
    font-size: 20px;
    background: linear-gradient(to bottom, #f5f5f5 0%, #ededed 100%);
`