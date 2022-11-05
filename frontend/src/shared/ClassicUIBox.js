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
    padding: ${props => props.padding ? props.padding : '20px'};
    padding-top: ${props => props.paddingTop ? props.paddingTop : '20px'};
    width: ${props => props.width ? props.width : '100%'};
    height: ${props => props.height || '100%'};
    min-height: ${props => props.minHeight || '100%'};
    display: ${props => props.display ? props.display : 'flex'};
    flex-direction: ${props => props.flexDirection ? props.flexDirection : 'column'};
    flex: ${props => props.flex ? props.flex : '1'};
    margin: auto;
    margin-bottom: 20px;
    gap: ${props => props.gap || '0px'};
    `;

export default ClassicUIBox;