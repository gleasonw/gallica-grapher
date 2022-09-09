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
        <div onClick={handleClick}>
            {expanded ?
                <BlurbExpand>
                    <OverflowYScrollTable>
                        <tbody>
                        {props.items.map((item, index) => {
                            return (
                                <tr key={index}>
                                    <td>{item}</td>
                                </tr>
                            )
                        })}
                        </tbody>
                    </OverflowYScrollTable>
                    {arrow}
                </BlurbExpand>
                :
                <span>
                    <BlurbText>
                        {props.shortenedItems}
                    </BlurbText>
                        + {props.numItemsRemaining} more
                </span>
            }
            {arrow}
        </div>
    )
}

const BlurbExpand = styled.div`
    position: absolute;
    background-color: white;
    overflow: visible;
    `;

const OverflowYScrollTable = styled(BlurbExpand)`
    border: 1px solid #d9d9d9;
    z-index: 1;
    tr:nth-child(even) {
        background-color: #;
    }
    position: absolute;
    max-height: 500px;
    max-width: 500px;
    overflow-y: scroll;
    `;