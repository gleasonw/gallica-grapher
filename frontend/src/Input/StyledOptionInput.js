import styled from "styled-components";

export const StyledOptionInput = styled.div`
    border: 2px solid #d9d9d9;
    border-radius: ${props => props.borderRadius || "10px 10px 0 0"};
    display: flex;
    flex-direction: ${props => props.flexDirection || "column"};}; 
`;