import styled from 'styled-components';

const PaperOptionWrap = styled.div`
    background-color: ${props => props.selected ? "#ffffff" : "rgba(255,255,255,0.0)"};
    color: ${props => props.selected ? "#4d4d4d" : "#d9d9d9"};
    border-bottom: ${props => props.borderBottom || "1px solid #d9d9d9"};
    padding: 12px 20px;
    text-align: left;
    cursor: pointer;
    transition: all 150ms;
    border-radius: ${props => props.borderRadius ? props.borderRadius : "0px"};
    position: relative;
    padding-bottom: ${props => props.paddingBottom || "12px"};
    `;

export default PaperOptionWrap;