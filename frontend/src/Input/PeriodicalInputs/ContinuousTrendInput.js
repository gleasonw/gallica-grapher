import React from "react";
import PaperOptionWrap from "./PaperOptionWrap";
import {DateInputBox} from "./DateInputBox";
import {KeyboardArrowDown} from "@mui/icons-material";
import {StyledArrow} from "./StyledArrow";

export function ContinuousTrendInput(props) {
    const lowYearPlaceholder = 1890;
    const highYearPlaceholder = 1920;
    const lowYear = props.yearRange[0];
    const highYear = props.yearRange[1];
    const onLowYearChange = props.yearRangeHandler[0];
    const onHighYearChange = props.yearRangeHandler[1];
    const dateInputs =
        <DateInputBox
            onLowDateChange={onLowYearChange}
            onHighDateChange={onHighYearChange}
            minYearPlaceholder={lowYearPlaceholder}
            maxYearPlaceholder={highYearPlaceholder}
            lowYear={lowYear}
            highYear={highYear}
            selected={props.selected === 0}
        />
    return (
        <PaperOptionWrap
            selected={props.selected === 0}
            onClick={() => props.onPaperSelectClick(0)}
            borderRadius={'10px 10px 0 0'}
        >
            <span className={'paperOptionHeader'}>
                {props.numContinuousPapers} continuous periodicals publishing
                every year between {dateInputs}
            </span>
            <StyledArrow
                bottom={'0'}
                top={'auto'}
                right={'0'}
            >
                {props.selected === 0 && <KeyboardArrowDown/>}
            </StyledArrow>
        </PaperOptionWrap>
    )
}