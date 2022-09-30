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
    height: 25px;
    width: 25px;
    position: absolute;
    top: 8px;
    right: 8px;
    `;