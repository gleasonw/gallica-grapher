import React from "react";
import useData from "../shared/hooks/useData";
import PaperOptionWrap from "./PaperOptionWrap";
import {DateInputBox} from "./DateInputBox";

export function ContinuousTrendInput(props) {
    const lowYearPlaceholder = 1890;
    const highYearPlaceholder = 1920;
    const lowYear = props.yearRange[0];
    const highYear = props.yearRange[1];
    const lowYearForDBQuery = lowYear ? lowYear : lowYearPlaceholder;
    const highYearForDBQuery = highYear ? highYear : highYearPlaceholder;
    const dateInputs =
        <DateInputBox
            onLowDateChange={(e) => props.onLowDateChange(e, 0)}
            onHighDateChange={(e) => props.onHighDateChange(e, 0)}
            minYearPlaceholder={lowYearPlaceholder}
            maxYearPlaceholder={highYearPlaceholder}
            lowYear={lowYear}
            highYear={highYear}
            selected={props.selected}
        />
    const [limit, setLimit] = React.useState(5000);
    const urlForContinuousPapers =
        "/api/continuousPapers" +
        "?limit=" + limit +
        "&startYear=" + lowYearForDBQuery +
        "&endYear=" + highYearForDBQuery;
    const result = useData(urlForContinuousPapers);
    let continuousPapers;
    if (result) {
        continuousPapers = result['paperNameCodes'];
    } else {
        continuousPapers = [];
    }
    return (
        <PaperOptionWrap
            selected={props.selected}
            onClick={() => props.onPaperSelectClick(0)}
        >
            <h5 className={'paperOptionHeader'}>
                In {continuousPapers.length ? continuousPapers.length : 0} periodicals publishing
                every year between {dateInputs}
            </h5>
        </PaperOptionWrap>
    )
}