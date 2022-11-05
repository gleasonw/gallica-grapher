import styled from "styled-components";

export const BlurbText = styled.div`
    padding: 10px;
    min-height: 42.5px;
    border-radius: 3px;
    font-size: 15px;
    background: #ece9e2;
    position: relative;
    max-width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    display: block;
    &:hover {
        white-space: normal;
        overflow: visible;
    }
`