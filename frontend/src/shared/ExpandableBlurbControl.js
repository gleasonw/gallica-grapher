import React, {useState} from "react";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ExpandLessIcon from "@mui/icons-material/ExpandLess";
import {BlurbText} from "./BlurbText";
import styled from "styled-components";
import {TextClipper} from "./TextClipper";

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
        <div onClick={handleClick}>
            <BlurbText>
                <TextClipper>
                {props.shortenedItems}
                </TextClipper>
            </BlurbText>
            {
                expanded ?
                <StyledPeriodicalDropdownTable>
                    <tbody>
                    {props.items.map((item) => (
                        <tr key={item}>
                            <td>{item}</td>
                        </tr>
                    ))}
                    </tbody>
                    {arrow}
                </StyledPeriodicalDropdownTable>
                    :
                <span>
                + {props.numItemsRemaining} more
                {arrow}
                </span>

            }
        </div>
    )
}

const StyledPeriodicalDropdownTable = styled.table`
    tr:nth-child(even){
        background-color: #f2f2f2;
    }
    max-width: 600px;
    max-height: 500px;
    td:hover{
        overflow: visible;
        white-space: normal;
        height: auto;
    }
    border-collapse: collapse;
    table-layout: fixed;
    position: absolute;
    z-index: 1;
    background-color: white;
    min-width: 140px;
    border-left: 1px solid #d9d9d9;
    border-right: 1px solid #d9d9d9;
    border-bottom: 1px solid #d9d9d9;
    `;

