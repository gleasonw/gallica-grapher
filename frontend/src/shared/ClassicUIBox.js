import styled from 'styled-components';

const ClassicUIBox = styled.div`
    box-shadow: rgba(0, 0, 0, 0.14) 0px 2px 2px 0px, rgba(0, 0, 0, 0.2) 0px 3px 1px -2px, rgba(0, 0, 0, 0.12) 0px 1px 5px 0px;    background-color: rgb(255, 255, 255);
    background-color: rgb(255, 255, 255);
    background-size: 100% 100%;
    color: rgb(77, 77, 77);
    border-bottom-left-radius: 3px;
    border-bottom-right-radius: 3px;
    border-top-left-radius: 3px;
    border-top-right-radius: 3px;
    padding: 30px;
    width: ${props => props.width || '100%'};
    height: ${props => props.height || '100%'};
    resize: ${props => props.resize ? props.resize : 'none'};
    `;

export default ClassicUIBox;