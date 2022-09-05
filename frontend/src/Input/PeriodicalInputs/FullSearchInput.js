import useData from "../../shared/hooks/useData";
import PaperOptionWrap from "./PaperOptionWrap";
import React from "react";
import {DateInputBox} from "./DateInputBox";

export function FullSearchInput(props) {
    const lowYearPlaceholder = 1499;
    const highYearPlaceholder = 2020;
    const lowYear = props.yearRange[0];
    const highYear = props.yearRange[1];
    let lowYearForDBQuery = lowYear ? lowYear : lowYearPlaceholder;
    let highYearForDBQuery = highYear ? highYear : highYearPlaceholder;
    const onLowDateChange = props.yearRangeHandler[0];
    const onHighDateChange = props.yearRangeHandler[1];
    const dateInputs =
        <DateInputBox
            onLowDateChange={onLowDateChange}
            onHighDateChange={onHighDateChange}
            minYearPlaceholder={lowYearPlaceholder}
            maxYearPlaceholder={highYearPlaceholder}
            lowYear={lowYear}
            highYear={highYear}
            selected={props.selected === 2}
        />
    const urlForPapersInRange =
        "/api/numPapersOverRange/" + lowYearForDBQuery + "/" + highYearForDBQuery;
    const result = useData(urlForPapersInRange);
    let numPapersOverRange;
    if (result) {
        numPapersOverRange = result['numPapersOverRange'];
    } else {
        numPapersOverRange = "0";
    }
    return (
        <PaperOptionWrap
            selected={props.selected === 2}
            borderBottom={'none'}
            onClick={() => props.onPaperSelectClick(2)}
        >
            <h5 className={'paperOptionHeader'}>
                {numPapersOverRange} periodicals publishing
                at any point between {dateInputs}
            </h5>
        </PaperOptionWrap>
    )
}