import styled from 'styled-components';

const DecorativeTicket = styled.div`
        display: flex;
        flex-direction: column;
        background-color: ${props => props.isMutable ? 'rgba(255, 255, 255, 0.5)' : 'rgb(255, 255, 255)'};
        padding: 15px;
        border-radius: ${props => props.borderRadius ? props.borderRadius : '10px'};
        border: 1px solid #d9d9d9;
        overflow: hidden;
        height: ${props => props.height ? props.height : 'auto'};
        max-width: ${props => props.maxWidth ? props.maxWidth : '100%'};
        flex: 1;
        position: relative;
        font-size: ${props => props.isMutable ? '15px' : '20px'};
    `;

export default DecorativeTicket;