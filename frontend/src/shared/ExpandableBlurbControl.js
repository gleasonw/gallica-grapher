import React, {useState} from "react";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ExpandLessIcon from "@mui/icons-material/ExpandLess";
import {BlurbText} from "./BlurbText";
import styled from "styled-components";

export function ExpandableBlurbControl(props) {
    const [expanded, setExpanded] = useState(false);
    const [arrow, setArrow] = useState(<ExpandMoreIcon/>);

    function handleClick() {
        setArrow(expanded ?
            <ExpandMoreIcon/> :
            <ExpandLessIcon/>
        )
        setExpanded(!expanded)
    }

    return (
        <StyledBlurbAndPlusLabel onClick={handleClick}>
            <BlurbText>{props.shortenedItems}</BlurbText>
            {
                expanded ?
                    <StyledPeriodicalDropdownTable>
                        {props.items.map((item) => (
                            <tr key={item}>
                                <td>{item}</td>
                            </tr>
                        ))}
                    </StyledPeriodicalDropdownTable>
                    :
                    <span>
                        + {props.numItemsRemaining} more
                        {arrow}
                    </span>

            }
        </StyledBlurbAndPlusLabel>
    )
}

const StyledBlurbAndPlusLabel = styled.div`
    min-height: 72.5px;
    cursor: pointer;
    position: relative;
    display: flex;
    flex-direction: column;
    max-width: 100%;
`;

const StyledPeriodicalDropdownTable = styled.div`
    td{
        padding: 10px;
        max-width: 400px;
    }
    tr:nth-child(even){
        background-color: #f2f2f2;
    }
    font-size: 14px;
    max-height: 100px;
    overflow-y: auto;
    top: 0;
    td:hover{
        overflow: visible;
        white-space: normal;
        height: auto;
    }
    background-color: white;
    min-width: 140px;
    border-left: 1px solid #d9d9d9;
    border-right: 1px solid #d9d9d9;
    border-bottom: 1px solid #d9d9d9;
    cursor: pointer;
    `;
