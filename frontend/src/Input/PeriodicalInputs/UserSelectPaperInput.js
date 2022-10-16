import OptionWrap from "../OptionWrap";
import {SelectionBox} from "../SelectionBox";
import {Dropdown} from "./Dropdown";
import React from "react";
import {KeyboardArrowDown} from "@mui/icons-material";
import {ShadowedFocusInput} from "../../shared/ShadowedFocusInput";

export function UserSelectPaperInput(props) {
    const paperNames = props.userSelectedPapers.map(paper => paper.title);
    const selected = props.selected === 1;
    return (
        <OptionWrap
            selected={selected}
            onClick={() => props.onPaperSelectClick(1)}
            paddingBottom={'40px'}
            onFocus={() => props.onFocus(1)}
        >
            <span className={'paperOptionHeader'}>
                My chosen periodicals
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
        </OptionWrap>

    )
}