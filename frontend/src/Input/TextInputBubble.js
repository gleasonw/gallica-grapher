import styled from 'styled-components';

const TextInputBubble = styled.div`
  font-size: large;
  position: relative;
  z-index: 1;
  max-width: ${props => props.maxWidth || "100%"};
  height: ${props => props.height || "auto"};
  padding: ${props => props.padding || "12px 20px"};
  align-items: center;
  cursor: pointer;
  border: ${props => props.noTermsReminder ? "2px solid red" : "2px solid #d9d9d9"};
  background-color: ${props => props.focus ? "white" : props.backgroundColor || "#ffffff"};
  border-radius: ${props => props.borderRadius || "10px"};
  color: #4d4d4d;
  transition: all 150ms;
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  box-shadow: ${props => props.focus ? "0 0 0 2px #575252" : "rgba(0, 0, 0, 0.075) 0px 1px 1px 0px inset"};
`;

export default TextInputBubble;