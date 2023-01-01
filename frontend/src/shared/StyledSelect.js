import styled from "styled-components";

export const StyledInputAndLabel = styled.div`
    display: ${props => props.display || "flex"};
    flex-direction: column;
    max-width: 100%;
    `;

export const StyledSelect = styled.select`
    padding: 5px;
    outline: none;
    background-color: inherit;
    box-shadow: rgba(0, 0, 0, 0.075) 0px 1px 1px 0px inset;
    cursor: pointer;
    border: 0.2rem solid #ece9e2;
    border-radius: 5px;
    color: #18181B;
    height: 42px;
    `;