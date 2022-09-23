import React from "react";
import styled from 'styled-components';
import {ContinuousTrendInput} from "./ContinuousTrendInput";
import {UserSelectPaperInput} from "./UserSelectPaperInput";
import {FullSearchInput} from "./FullSearchInput";

export class PaperInputBox extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            timerForSpacingAjaxRequests: null,
            papersForDropdown: [],
            dropdownError: null,
            paperInputValue: '',
        }
        this.handleKeyUp = this.handleKeyUp.bind(this);
        this.handleDropdownClick = this.handleDropdownClick.bind(this);
        this.handlePaperChange = this.handlePaperChange.bind(this);
    }

    handlePaperChange(event) {
        this.setState({paperInputValue: event.target.value})
    }

    handleKeyUp(event) {
        clearTimeout(this.state.timerForSpacingAjaxRequests);
        if (event.target.value) {
            this.setState({
                    timerForSpacingAjaxRequests:
                        setTimeout(() => {
                            this.getPaperDropdownItems(event.target.value)
                        }, 500)
                }
            );
        } else {
            this.setState({
                papersForDropdown: [],
            })
        }
    }

    getPaperDropdownItems(searchString) {
        fetch("/api/papers/" + searchString)
            .then(res => res.json())
            .then(
                (result) => {
                    this.setState({
                        dropdownError: null,
                        papersForDropdown: result
                    });
                },
                (dropdownError) => {
                    this.setState({
                        dropdownError
                    })

                }
            )
    }

    handleDropdownClick(paperNameCode) {
        this.props.onClick(paperNameCode);
        this.setState({
            papersForDropdown: [],
            paperInputValue: '',
        })
    }

    render() {
        return (
            <StyledPaperInput
                padding={"0"}
                backgroundColor={"#f5f5f5"}
                borderRadius={"10px 10px 0 0"}
            >
                <ContinuousTrendInput
                    yearRange={this.props.dateRanges[0]}
                    yearRangeHandler={this.props.dateRangeHandlers[0]}
                    selected={this.props.selectedPaperInput}
                    onPaperSelectClick={this.props.onPaperInputSelectClick}
                    numContinuousPapers={this.props.numContinuousPapers}
                    onFocus={this.props.onFocus}
                />
                <UserSelectPaperInput
                    yearRange={this.props.dateRanges[1]}
                    yearRangeHandler={this.props.dateRangeHandlers[1]}
                    boundaryYearsForUserPapers={this.props.boundaryYearsForUserPapers}
                    deletePaperBubble={this.props.deletePaperBubble}
                    paperInputValue={this.state.paperInputValue}
                    onKeyUp={this.handleKeyUp}
                    onPaperChange={this.handlePaperChange}
                    papersForDropdown={this.state.papersForDropdown}
                    onClick={this.handleDropdownClick}
                    error={this.state.dropdownError}
                    onDropdownClick={this.handleDropdownClick}
                    selected={this.props.selectedPaperInput}
                    onPaperSelectClick={this.props.onPaperInputSelectClick}
                    userSelectedPapers={this.props.userSelectedPapers}
                    onFocus={this.props.onFocus}
                />
                <FullSearchInput
                    yearRange={this.props.dateRanges[2]}
                    yearRangeHandler={this.props.dateRangeHandlers[2]}
                    selected={this.props.selectedPaperInput}
                    onPaperSelectClick={this.props.onPaperInputSelectClick}
                    onFocus={this.props.onFocus}
                />
            </StyledPaperInput>
        )
    }
}

const StyledPaperInput = styled.div`
    border: 2px solid #d9d9d9;
    border-radius: 10px 10px 0 0;

`;

