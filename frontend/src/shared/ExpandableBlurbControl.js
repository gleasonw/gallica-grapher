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
        <StyledBlurbAndPlusLabel onClick={handleClick}>
            <BlurbText>
                <TextClipper>
                {props.shortenedItems}
                </TextClipper>
            </BlurbText>
            {
                expanded ?
                    <StyledDrop>
                        <table>
                            <StyledPeriodicalDropdownTable>
                                {props.items.map((item) => (
                                    <tr key={item}>
                                        <td>{item}</td>
                                    </tr>
                                ))}
                            </StyledPeriodicalDropdownTable>
                        </table>
                    </StyledDrop>
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
`;

const StyledReduceArrow = styled.div`
    position: absolute;
    bottom: 0;
    right: 50%;
    z-index: 2;
`;

const StyledPeriodicalDropdownTable = styled.tbody`
    td{
        padding: 10px;
    }
    tr:nth-child(even){
        background-color: #f2f2f2;
    }
    font-size: 14px;
    max-width: 600px;
    overflow-y: scroll;
    max-height: 300px;
    td:hover{
        overflow: visible;
        white-space: normal;
        height: auto;
    }
    position: absolute;
    z-index: 1;
    background-color: white;
    min-width: 140px;
    border-left: 1px solid #d9d9d9;
    border-right: 1px solid #d9d9d9;
    border-bottom: 1px solid #d9d9d9;
    cursor: pointer;
    `;

const StyledDrop = styled.div`
    position: relative;
    width: 599px;
`;

