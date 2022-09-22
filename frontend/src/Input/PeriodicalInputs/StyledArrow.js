import styled from 'styled-components';

export const StyledArrow = styled.div`
    align-self: center;
    display: flex;
    position: absolute;
    right: ${props => props.right || "0px"};
    top: ${props => props.top || "0px"};
    bottom: ${props => props.bottom || "0px"};
    color: #4d4d4d;
    font-size: 1.5rem;
    min-height: 24px;
    padding: 15px;
    `;