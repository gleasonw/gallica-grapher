import React, {useState} from 'react';
import DateGroupSelect from './DateGroupSelect.js';
import DateRangeSelect from './DateRangeSelect.js';
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
                <StyledLabel>View occurrences of this word:</StyledLabel>
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
                    <StyledLabel>in these periodicals:</StyledLabel>
                    <PaperInputBox
                        onClick={props.onPaperDropItemClick}
                        deletePaperBubble={props.deletePaperBubble}
                        onPaperInputSelectClick={props.onPaperInputClick}
                        selectedPaperInput={props.selectedPaperInput}
                        numContinuousPapers={props.numContinuousPapers}
                        userSelectedPapers={props.userSelectedPapers}
                        boundaryYearsForUserPapers={props.boundaryYearsForUserPapers}
                        onFocus={props.onPaperInputFocus}
                        startYear={props.startYear}
                        endYear={props.endYear}
                    />
                    <div ref={props.requestBoxRef}>
                        <StyledRequestBox
                            tickets={props.tickets}
                            onTicketClick={props.onTicketClick}
                            className={'requestBox'}
                            onCreateTicketClick={handleCreateTicketClick}
                            mismatchedDataOrigin={props.mismatchedDataOrigin}
                        />
                    </div>
                </StyledLabeledInput>
            </div>
            <StyledLabeledInput>
                <StyledLabel>between:</StyledLabel>
                <DateRangeSelect
                    startYear={props.startYear}
                    endYear={props.endYear}
                    onStartYearChange={props.onStartYearChange}
                    onEndYearChange={props.onEndYearChange}
                    selectedPaperBoundary={props.boundaryYearsForUserPapers}
                    justifyContent={'space-between'}
                    flexDirection={'row'}
                />
            </StyledLabeledInput>
            <StyledLabeledInput>
                <StyledLabel>grouped by: </StyledLabel>
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
    gap: 20px;
    width: calc(100% - 2rem);
    max-width: 800px;
`;

const StyledLabeledInput = styled.div`
  display: flex;
  flex-direction: column;
  font-size: 1.2rem;
  margin-top: 20px;
  margin-bottom: 20px;
`;

const StyledLabel = styled.label`
    font-size: 1.2rem;
    margin-bottom: 20px;
    color: #18181B;
`;

export default TicketForm;