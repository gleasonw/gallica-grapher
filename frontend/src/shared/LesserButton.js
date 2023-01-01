import styled from 'styled-components';

const LesserButton = styled.div`
    position: ${props => props.position ? props.position : 'relative'};
    z-index: ${props => props.zIndex ? props.zIndex : '0'};
    cursor: pointer;
    text-align: center;
    background: linear-gradient(to bottom, #f5f5f5 0%, #ededed 100%);
    text-shadow: 0 1px 0 #fff;
    border: 1px solid #d9d9d9;
    transition: all 150ms;
    color: #18181B;
    border-radius: ${props => props.borderRadius || "10px"};
    border-top: ${props => props.borderTop || "1px solid #d9d9d9"};
    font-size: 15px;
    max-width: 200px;
    min-width: 122px;
    max-height: 50px;
    padding: 10px;
    margin-left: ${props => props.marginLeft || "0px"};
    margin-right: ${props => props.marginRight || "0px"};
    &:hover{
        background: linear-gradient(to bottom, #ededed 0%, #f5f5f5 100%);
        color: #787878;
        }
    width: ${props => props.width || "auto"};
    `;

export default LesserButton;