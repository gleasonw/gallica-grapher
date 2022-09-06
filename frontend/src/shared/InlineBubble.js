import styled from 'styled-components';

const InlineBubble = styled.div`
    font-size: large;
    height: 40px;
    padding: 10px;
    outline: none;
    appearance: none;
    cursor: pointer;
    color: ${props => props.selected ? "#4d4d4d" : "#d9d9d9"};
    border: ${props => props.selected ? "1px solid #4d4d4d" : "1px solid #d9d9d9"};
    background-color: ${props => props.selected ? "rgba(255,255,255,0.5)" : ""};
    border-radius: 10px;
    transition: all 150ms;
    overflow: hidden;
    `;

export default InlineBubble;