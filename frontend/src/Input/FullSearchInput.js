import useData from "../shared/hooks/useData";
import PaperOptionWrap from "./PaperOptionWrap";
import React from "react";
import {DateInputBox} from "./DateInputBox";

export function FullSearchInput(props) {
    const lowYearPlaceholder = 1499;
    const highYearPlaceholder = 2020;
    const lowYear = props.yearRange[0];
    const highYear = props.yearRange[1];
    const lowYearForDBQuery = lowYear ? lowYear : lowYearPlaceholder;
    const highYearForDBQuery = highYear ? highYear : highYearPlaceholder;
    const dateInputs =
        <DateInputBox
            onLowDateChange={(e) => props.onLowDateChange(e, 2)}
            onHighDateChange={(e) => props.onHighDateChange(e, 2)}
            minYearPlaceholder={lowYearPlaceholder}
            maxYearPlaceholder={highYearPlaceholder}
            lowYear={lowYear}
            highYear={highYear}
            selected={props.selected}
        />
    const urlForPapersInRange =
        "/api/numPapersOverRange/" + lowYearForDBQuery + "/" + highYearForDBQuery;
    const result = useData(urlForPapersInRange);
    let numPapersOverRange;
    if (result) {
        numPapersOverRange = result['numPapersOverRange'];
    } else {
        numPapersOverRange = "...";
    }
    return (
        <PaperOptionWrap
            selected={props.selected}
            borderBottom={'none'}
            onClick={() => props.onPaperSelectClick(2)}
        >
            <h5 className={'paperOptionHeader'}>
                In {numPapersOverRange} periodicals publishing
                at any point between {dateInputs}
            </h5>
        </PaperOptionWrap>
    )
}