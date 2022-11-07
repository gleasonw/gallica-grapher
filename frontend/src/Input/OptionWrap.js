import styled from 'styled-components';

const OptionWrap = styled.div`
    background-color: ${props => props.selected ? "#ffffff" : "rgba(255,255,255,0.0)"};
    color: ${props => props.selected ? "#4d4d4d" : "#b3b3b3"};
    border-bottom: ${props => props.borderBottom || "1px solid #d9d9d9"};
    padding: 12px 20px;
    font-size: 20px;
    text-align: left;
    width: 100%;
    cursor: pointer;
    transition: all 150ms;
    border-radius: ${props => props.borderRadius ? props.borderRadius : "0px"};
    position: relative;
    padding-bottom: ${props => props.paddingBottom || "12px"};
    &:hover{
        background-color: ${props => props.selected ? "#ffffff" : "rgba(255,255,255,0.2)"};
    }
    display: ${props => props.display || "block"};
    align-items: center;
    justify-content: ${props => props.justifyContent || "flex-start"};
    `;

export default OptionWrap;