import PaperOptionWrap from "./PaperOptionWrap";
import {SelectionBox} from "../SelectionBox";
import {Dropdown} from "./Dropdown";
import React from "react";
import {DateInputBox} from "./DateInputBox";

export function UserSelectPaperInput(props) {
    const dateInput =
        <DateInputBox
            onLowDateChange={(e) => props.onLowDateChange(e, 1)}
            onHighDateChange={(e) => props.onHighDateChange(e, 1)}
            minYearPlaceholder={1890}
            maxYearPlaceholder={1920}
            lowYear={props.yearRange[0]}
            highYear={props.yearRange[1]}
            selected={props.selected === 1}
        />
    return (
        <PaperOptionWrap
            selected={props.selected === 1}
            onClick={() => props.onPaperSelectClick(1)}
        >
            <h5 className={'paperOptionHeader'}>
                In these periodicals between {dateInput}
            </h5>
            <SelectionBox
                items={props.paperNames}
                onClick={props.deletePaperBubble}
            />
            <input
                type="text"
                value={props.paperInputValue}
                name="papers"
                placeholder="Enter a paper to restrict search..."
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