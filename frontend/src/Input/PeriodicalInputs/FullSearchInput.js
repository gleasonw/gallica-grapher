import useData from "../../shared/hooks/useData";
import OptionWrap from "../OptionWrap";
import React from "react";

export function FullSearchInput(props) {
    const urlForPapersInRange = `/api/numPapersOverRange/${props.startYear}/${props.endYear}`;
    const numPapersOverRange = useData(urlForPapersInRange);
    return (
        <OptionWrap
            selected={props.selected === 2}
            borderBottom={'none'}
            onClick={() => props.onPaperSelectClick(2)}
            borderRadius={'10px 10px 0 0'}
            onFocus={() => props.onFocus(2)}
        >
            <span className={'paperOptionHeader'}>
                {numPapersOverRange || '...'} periodicals publishing
                at any point
            </span>
        </OptionWrap>
    )
}