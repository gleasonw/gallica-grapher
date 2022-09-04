import React from "react";
import PaperOptionWrap from "./PaperOptionWrap";
import {DateInputBox} from "./DateInputBox";

export function ContinuousTrendInput(props) {
    const lowYearPlaceholder = 1890;
    const highYearPlaceholder = 1920;
    const lowYear = props.yearRange[0];
    const highYear = props.yearRange[1];
    const dateInputs =
        <DateInputBox
            onLowDateChange={(e) => props.onLowDateChange(e, 0)}
            onHighDateChange={(e) => props.onHighDateChange(e, 0)}
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
        >
            <h5 className={'paperOptionHeader'}>
                In {props.numContinuousPapers} periodicals publishing
                every year between {dateInputs}
            </h5>
        </PaperOptionWrap>
    )
}