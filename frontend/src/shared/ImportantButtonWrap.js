import styled from 'styled-components';

const ImportantButtonWrap = styled.button`
    text-align: center;
    align-self: center;
    cursor: pointer;
    background: linear-gradient(to bottom, #f5f5f5 0%, #ededed 100%);
    text-shadow: 0 1px 0 #fff;
    box-shadow: 0 2px 5px 0 rgba(0,0,0,0.225);
    transition: all 150ms;
    color: #4d4d4d;
    border-radius: 10px;
    font-size: 30px;
    padding: 20px;
    margin: 10px;
    border: 1px solid #c6c6c6;
    @media screen and (max-width: 748px){
        font-size: 15px;
        }
    &:hover{
        background: linear-gradient(to bottom, #ededed 0%, #f5f5f5 100%);
        color: #787878;
        }
    `;

export default ImportantButtonWrap;