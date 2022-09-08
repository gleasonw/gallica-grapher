import styled from 'styled-components';

const TextInputBubble = styled.div`
    font-size: large;
    max-width: ${props => props.maxWidth || "100%"};
    height: ${props => props.height || "auto"};
    padding: ${props => props.padding || "12px 20px"};
    justify-content: center;
    align-items: center;
    cursor: pointer;
    border: ${props => props.noTermsReminder ?  "1px solid #ff0000": "1px solid #d9d9d9"};
    background-color: ${props => props.backgroundColor || "#ffffff"};
    border-radius: ${props => props.borderRadius || "10px"};
    color: #4d4d4d;
    transition: all 150ms;
    `;

export default TextInputBubble;