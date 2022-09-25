import styled from 'styled-components';

const DecorativeTicket = styled.div`
        display: flex;
        flex-direction: column;
        background-color: rgba(255, 255, 255, 0.5);
        padding: 15px;
        border-radius: ${props => props.borderRadius ? props.borderRadius : '10px'};
        border: 1px solid #d9d9d9;
        overflow: hidden;
        height: ${props => props.height ? props.height : 'auto'};
        max-width: ${props => props.maxWidth ? props.maxWidth : '100%'};
        flex: 1;
        position: relative;
    `;

export default DecorativeTicket;