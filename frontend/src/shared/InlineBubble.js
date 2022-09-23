import styled from 'styled-components';

const InlineBubble = styled.div`
    padding: 5px;
    outline: none;
    appearance: none;
    color: ${props => props.selected ? "#4d4d4d" : "#d9d9d9"};
    border: ${props => props.selected ? "0.2rem solid #ece9e2" : 'none'};
    border-radius: 5px;
    ${props => props.selected && !props.focus ? `&:hover{
        border-color: #c6c6c6;
        background-color: #e6e6e6;
    }` : ''}
    box-shadow: ${props => props.focus ? "0 0 0 2px #575252" : "rgba(0, 0, 0, 0.075) 0px 1px 1px 0px inset"};
    `;

export default InlineBubble;