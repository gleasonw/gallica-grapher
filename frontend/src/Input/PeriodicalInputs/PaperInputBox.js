import React from "react";
import TextInputBubble from "../TextInputBubble";
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
            selectedInput: [1, 0, 0],
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

    //TODO: reduce duplication in paperinput options
    render() {
        return (
            <TextInputBubble
                padding={"0"}
                backgroundColor={"#f5f5f5"}
            >
                <ContinuousTrendInput
                    yearRange={this.props.dateRanges[0]}
                    yearRangeHandler={this.props.dateRangeHandlers[0]}
                    selected={this.props.selectedPaperInput}
                    onPaperSelectClick={this.props.onPaperInputSelectClick}
                    numContinuousPapers={this.props.numContinuousPapers}

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
                />
                <FullSearchInput
                    yearRange={this.props.dateRanges[2]}
                    yearRangeHandler={this.props.dateRangeHandlers[2]}
                    selected={this.props.selectedPaperInput}
                    onPaperSelectClick={this.props.onPaperInputSelectClick}
                />
            </TextInputBubble>
        )
    }
}

