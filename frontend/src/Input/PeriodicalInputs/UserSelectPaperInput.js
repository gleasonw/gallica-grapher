import OptionWrap from "../OptionWrap";
import {SelectionBox} from "../SelectionBox";
import {Dropdown} from "./Dropdown";
import React from "react";
import {DateInputBox} from "./DateInputBox";
import {KeyboardArrowDown} from "@mui/icons-material";
import {StyledArrow} from "./StyledArrow";
import {KeyboardArrowUp} from "@mui/icons-material";
import {ShadowedFocusInput} from "../../shared/ShadowedFocusInput";

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
    const selected = props.selected === 1;
    return (
        <OptionWrap
            selected={selected}
            onClick={() => props.onPaperSelectClick(1)}
            paddingBottom={'40px'}
            onFocus={() => props.onFocus(1)}
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
                <ShadowedFocusInput
                    type={'text'}
                    id={selected ? "selectedPaperInput": "unselectedPaperInput"}
                    name={'papers'}
                    placeholder={'Enter a periodical name'}
                    onKeyUp={props.onKeyUp}
                    onChange={props.onPaperChange}
                    value={props.paperInputValue}
                    autoComplete={'off'}
                    selected={selected}
                />
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
        </OptionWrap>

    )
}