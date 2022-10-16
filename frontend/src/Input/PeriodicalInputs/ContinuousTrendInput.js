import React from "react";
import OptionWrap from "../OptionWrap";
import {KeyboardArrowDown} from "@mui/icons-material";
import {StyledArrow} from "./StyledArrow";

export function ContinuousTrendInput(props) {
    return (
        <OptionWrap
            selected={props.selected === 0}
            onClick={() => props.onPaperSelectClick(0)}
            onFocus={() => props.onFocus(0)}
            borderRadius={'0'}
        >
            <span className={'paperOptionHeader'}>
                {props.numContinuousPapers} continuous periodicals publishing every year
            </span>
        </OptionWrap>
    )
}