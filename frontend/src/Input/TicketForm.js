import React, {useState} from 'react';
import DateGroupSelect from './DateGroupSelect.tsx';
import DateSelect from './DateSelect.tsx';
import ImportantButtonWrap from "../shared/ImportantButtonWrap";
import {StyledRequestBox} from "./RequestBox";
import {PaperInputBox} from "./PeriodicalInputs/PaperInputBox";
import {TermInputBox} from "./TermInputBox";
import RequestBoxAndFetchButtonWrap from "./RequestBoxAndFetchButtonWrap";
import styled from "styled-components";

function TicketForm(props) {
    const [showNoTermsReminder, setShowNoTermsReminder] = useState(false);

    function handleSubmit(e) {
        e.preventDefault();
        if ((!props.tickets || Object.keys(props.tickets).length === 0)
            &&
            (props.termInput === '')) {
            setShowNoTermsReminder(true)
        } else {
            props.onSubmit(e);
        }
    }

    function handleCreateTicketClick() {
        if (props.termInput !== '') {
            props.onCreateTicketClick();
        } else {
            setShowNoTermsReminder(true);
        }
    }

    function handleTermChange(e) {
        setShowNoTermsReminder(false);
        props.handleTermChange(e);
    }

    return (
        <StyledTicketForm onSubmit={handleSubmit}>
            <StyledLabeledInput>
                <label>View occurrences of this word:</label>
                <TermInputBox
                    onEnterPress={handleSubmit}
                    selectedTerms={props.selectedTerms}
                    deleteTermBubble={props.deleteTermBubble}
                    termInput={props.termInput}
                    handleTermChange={handleTermChange}
                    noTermsReminder={showNoTermsReminder}
                    linkTerm={props.linkTerm}
                    linkDistance={props.linkDistance}
                    onLinkTermChange={props.onLinkTermChange}
                    onLinkDistanceChange={props.onLinkDistanceChange}
                />
            </StyledLabeledInput>
            <div>
                <StyledLabeledInput>
                    <label>in these periodicals:</label>
                    <PaperInputBox
                        onClick={props.onPaperDropItemClick}
                        deletePaperBubble={props.deletePaperBubble}
                        onPaperInputSelectClick={props.onPaperInputClick}
                        selectedPaperInput={props.selectedPaperInput}
                        numContinuousPapers={props.numContinuousPapers}
                        userSelectedPapers={props.userSelectedPapers}
                        boundaryYearsForUserPapers={props.boundaryYearsForUserPapers}
                        onFocus={props.onPaperInputFocus}
                        startDate={props.startDate}
                        endDate={props.endDate}
                    />
                </StyledLabeledInput>
                <div ref={props.requestBoxRef}>
                    <StyledRequestBox
                        tickets={props.tickets}
                        onTicketClick={props.onTicketClick}
                        className={'requestBox'}
                        onCreateTicketClick={handleCreateTicketClick}
                    />
                </div>
            </div>
            <StyledLabeledInput>
                <label>between:</label>
                <DateSelect
                    startDate={props.startDate}
                    endDate={props.endDate}
                    onstartDateChange={props.onstartDateChange}
                    onendDateChange={props.onendDateChange}
                    selectedPaperBoundary={props.boundaryYearsForUserPapers}
                />
                <label>grouped by: </label>
                <DateGroupSelect
                    selectedSearchType={props.selectedSearchType}
                    onDateGroupClick={props.onSearchTypeClick}
                    selected={props.selectedSearchType}
                />
            </StyledLabeledInput>
            <RequestBoxAndFetchButtonWrap>
                <ImportantButtonWrap>
                    <input
                        type='submit'
                        value='Fetch and graph 📊'
                    />
                </ImportantButtonWrap>
            </RequestBoxAndFetchButtonWrap>
        </StyledTicketForm>
    )
}

const StyledTicketForm = styled.form`
    display: flex;
    flex-direction: column;
    padding: 1rem;
    gap: 1rem;
    width: calc(100% - 2rem);
    max-width: 800px;
`;

const StyledLabeledInput = styled.div`
    display: flex;
    flex-direction: column;
    gap: 1rem;
    font-size: 1.2rem;
`;

export default TicketForm;