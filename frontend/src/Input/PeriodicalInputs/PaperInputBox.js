import React from "react";
import {UserSelectPaperInput} from "./UserSelectPaperInput";
import {FullSearchInput} from "./FullSearchInput";
import {StyledOptionInput} from "../StyledOptionInput";

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
            <StyledOptionInput
                padding={"0"}
                backgroundColor={"#f5f5f5"}
                borderRadius={"10px 10px 0 0"}
            >
                <FullSearchInput
                    selected={this.props.selectedPaperInput}
                    onPaperSelectClick={this.props.onPaperInputSelectClick}
                    onFocus={this.props.onFocus}
                    startYear={this.props.startYear}
                    endYear={this.props.endYear}
                />
                <UserSelectPaperInput
                    deletePaperBubble={this.props.deletePaperBubble}
                    paperInputValue={this.state.paperInputValue}
                    onFocus={this.props.onFocus}
                    onKeyUp={this.handleKeyUp}
                    startDate={this.props.startDate}
                    endDate={this.props.endDate}
                    onPaperChange={this.handlePaperChange}
                    papersForDropdown={this.state.papersForDropdown}
                    onClick={this.handleDropdownClick}
                    error={this.state.dropdownError}
                    onDropdownClick={this.handleDropdownClick}
                    selected={this.props.selectedPaperInput}
                    onPaperSelectClick={this.props.onPaperInputSelectClick}
                    userSelectedPapers={this.props.userSelectedPapers}
                />
            </StyledOptionInput>
        )
    }
}

