import styled from 'styled-components';

const InlineBubble = styled.div`
    padding: 5px;
    outline: none;
    appearance: none;
    color: ${props => props.selected ? "#4d4d4d" : "#d9d9d9"};
    border: 0.2rem solid #ece9e2;
    border-radius: 5px;
    transition: all 50ms;
    ${props => props.focus ? '' : `&:hover{
        border-color: #c6c6c6;
        background-color: #e6e6e6;
    }`}
    &:focus{
        background-color: rgba(255,255,255,0.5);
    }
    `;

export default InlineBubble;