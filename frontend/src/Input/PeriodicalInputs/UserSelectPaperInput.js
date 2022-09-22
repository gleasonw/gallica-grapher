import PaperOptionWrap from "./PaperOptionWrap";
import {SelectionBox} from "../SelectionBox";
import {Dropdown} from "./Dropdown";
import React from "react";
import {DateInputBox} from "./DateInputBox";
import {KeyboardArrowDown} from "@mui/icons-material";
import {StyledArrow} from "./StyledArrow";
import {KeyboardArrowUp} from "@mui/icons-material";
import InlineBubble from "../../shared/InlineBubble";

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
            paddingBottom={'40px'}
        >
            <StyledArrow>
                {props.selected === 1 && <KeyboardArrowUp/>}
            </StyledArrow>
            <span className={'paperOptionHeader'}>
                My chosen periodicals between {dateInput}
            </span>
            <SelectionBox
                items={paperNames}
                onClick={props.deletePaperBubble}
            />
            <div className={'paperSelectInputWrap'}>
                <InlineBubble>
                    <input
                        type="text"
                        id={props.selected === 1 ? "selectedPaperInput" : "unselectedPaperInput"}
                        value={props.paperInputValue}
                        name="papers"
                        placeholder="Search for a periodical"
                        onKeyUp={props.onKeyUp}
                        onChange={props.onPaperChange}
                        autoComplete="off"
                    />
                </InlineBubble>
            </div>
            <div className='dropdownContainer'>
                <Dropdown
                    papers={props.papersForDropdown['paperNameCodes']}
                    error={props.dropdownError}
                    onClick={props.onDropdownClick}
                />
            </div>
            <StyledArrow
                bottom={'0'}
                top={'auto'}
                right={'0'}
            >
                {props.selected === 1 && <KeyboardArrowDown/>}
            </StyledArrow>
        </PaperOptionWrap>

    )
}