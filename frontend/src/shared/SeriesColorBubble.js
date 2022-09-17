import styled from "styled-components";


export default function SeriesColorBubble(props){
    return(
        <StyledSeriesColorBubble
            color={props.color}
        />
    )
}

const StyledSeriesColorBubble = styled.div`
    background-color: ${props => props.color};
    border-radius: 50%;
    height: 20px;
    width: 20px;
    position: absolute;
    top: 5px;
    right: 5px;
    `;