import styled from "styled-components";

export const BlurbText = styled.section`
    max-width: 110px;
    max-height: 180px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: ${props => props.expanded ? 'wrap' : 'nowrap'};
    z-index: ${props => props.expanded ? '1' : '0'};
    padding: 10px;
    border-radius: 3px;
    font-size: 15px;
    background: linear-gradient(to bottom, #f5f5f5 0%, #ededed 100%);
`