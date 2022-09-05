import PaperOptionWrap from "./PaperOptionWrap";
import {SelectionBox} from "../SelectionBox";
import {Dropdown} from "./Dropdown";
import React from "react";
import {DateInputBox} from "./DateInputBox";

export function UserSelectPaperInput(props) {
    const onLowDateChange = props.yearRangeHandler[0];
    const onHighDateChange = props.yearRangeHandler[1];
    const dateInput =
        <DateInputBox
            onLowDateChange={onLowDateChange}
            onHighDateChange={onHighDateChange}
            minYearPlaceholder={props.boundaryYearsForUserPapers[0]}
            maxYearPlaceholder={props.boundaryYearsForUserPapers[1]}
            lowYear={props.yearRange[0]}
            highYear={props.yearRange[1]}
            selected={props.selected === 1}
        />
    const paperNames = props.userSelectedPapers.map(paper => paper.title);
    return (
        <PaperOptionWrap
            selected={props.selected === 1}
            onClick={() => props.onPaperSelectClick(1)}
        >
            <h5 className={'paperOptionHeader'}>
                My chosen periodicals between {dateInput}
            </h5>
            <SelectionBox
                items={paperNames}
                onClick={props.deletePaperBubble}
            />
            <input
                type="text"
                value={props.paperInputValue}
                name="papers"
                placeholder="Search for a periodical"
                onKeyUp={props.onKeyUp}
                onChange={props.onPaperChange}
                autoComplete="off"
            />
            <div className='dropdownContainer'>
                <Dropdown
                    papers={props.papersForDropdown['paperNameCodes']}
                    error={props.dropdownError}
                    onClick={props.onDropdownClick}
                />
            </div>
        </PaperOptionWrap>

    )
}