import React from "react";
import TextInputBubble from "./TextInputBubble";
import LesserButton from "../shared/LesserButton";
import AddLinkIcon from '@mui/icons-material/AddLink';
import {ShadowedFocusInput} from "../shared/ShadowedFocusInput";
import NavBarWrap from "../Result/NavBarWrap";


export function TermInputBox(props) {
    const [focus, setFocus] = React.useState(false);
    const [showLinkedSearch, setShowLinkedSearch] = React.useState(false);

    function handleKeyDown(event) {
        if (event.key === 'Enter') {
            props.onEnterPress(event)
        }
    }

    return (
        <div>
            <TextInputBubble
                noTermsReminder={props.noTermsReminder}
                focus={focus}
                borderRadius={'10px 10px 10px 0px'}
            >
                <input
                    autoFocus
                    type="text"
                    value={props.termInput}
                    name="updatedTerms"
                    placeholder={props.noTermsReminder ? "Please enter a word" : "Enter a word"}
                    onChange={props.handleTermChange}
                    onKeyDown={handleKeyDown}
                    autoComplete="off"
                    onFocus={() => setFocus(true)}
                    onBlur={() => setFocus(false)}
                />
            </TextInputBubble>
            {showLinkedSearch &&
                <NavBarWrap>
                    when it appears within
                    <ShadowedFocusInput
                        selected
                        id={'linkDistance'}
                        value={props.linkDistance}
                        onChange={props.onLinkDistanceChange}
                        type={'number'}
                        min={0}
                        placeholder={'10'}
                        width={'50px'}
                        backgroundColor={'white'}
                    />
                    words of
                    <ShadowedFocusInput
                        id={'linkTerm'}
                        value={props.linkTerm}
                        onChange={props.onLinkTermChange}
                        selected
                        type={'text'}
                        placeholder={'another word'}
                        backgroundColor={'white'}
                    />
                </NavBarWrap>
            }
            <LesserButton
                onClick={() => setShowLinkedSearch(!showLinkedSearch)}
                borderRadius="0px 0px 10px 10px"
                width={'30px'}
                borderTop={''}
                zIndex={0.5}
            >
                <AddLinkIcon/>
                Link
            </LesserButton>

        </div>
    )
}