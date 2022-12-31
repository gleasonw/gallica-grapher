import useData from "../../shared/hooks/useData";
import OptionWrap from "../OptionWrap";
import React from "react";

export function FullSearchInput(props) {
    const urlForPapersInRange = `${process.env.REACT_APP_API_URL}/api/numPapersOverRange/${props.startYear || 0}/${props.endYear || 0}`;
    const numPapersInRange = useData(urlForPapersInRange);
    return (
        <OptionWrap
            selected={props.selected === 2}
            borderBottom={'none'}
            onClick={() => props.onPaperSelectClick(2)}
            borderRadius={'10px 10px 0 0'}
            onFocus={() => props.onFocus(2)}
        >
            <span className={'paperOptionHeader'}>
                {numPapersInRange || '...'} periodicals publishing
                at any point
            </span>
        </OptionWrap>
    )
}
