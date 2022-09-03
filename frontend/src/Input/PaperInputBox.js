import React from "react";
import TextInputBubble from "./TextInputBubble";
import {ContinuousTrendInput} from "./ContinuousTrendInput";
import {PaperArrayInput} from "./PaperArrayInput";
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
        this.handlePaperSelectClick = this.handlePaperSelectClick.bind(this);
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

    handlePaperSelectClick(index) {
        const newSelectedInput = [0, 0, 0];
        newSelectedInput[index] = 1;
        this.setState({
            selectedInput: newSelectedInput
        })
    }
    //TODO: reduce duplication in paperinput options
    render() {
        const paperNames = [];
        this.props.selectedPapers.map(paperAndCode => paperNames.push(paperAndCode['title']))
        return (
            <TextInputBubble
                padding={"0"}
            >
                <ContinuousTrendInput
                    yearRange={this.props.dateRanges[0]}
                    selected={this.state.selectedInput[0]}
                    onPaperSelectClick={this.handlePaperSelectClick}
                    onLowDateChange={this.props.onLowDateChange}
                    onHighDateChange={this.props.onHighDateChange}
                />
                <PaperArrayInput
                    yearRange={this.props.dateRanges[1]}
                    paperNames={paperNames}
                    deletePaperBubble={this.props.deletePaperBubble}
                    paperInputValue={this.state.paperInputValue}
                    onKeyUp={this.handleKeyUp}
                    onPaperChange={this.handlePaperChange}
                    papersForDropdown={this.state.papersForDropdown}
                    onClick={this.handleDropdownClick}
                    error={this.state.dropdownError}
                    onDropdownClick={this.handleDropdownClick}
                    selected={this.state.selectedInput[1]}
                    onPaperSelectClick={this.handlePaperSelectClick}
                    onLowDateChange={this.props.onLowDateChange}
                    onHighDateChange={this.props.onHighDateChange}
                />
                <FullSearchInput
                    yearRange={this.props.dateRanges[2]}
                    selected={this.state.selectedInput[2]}
                    onPaperSelectClick={this.handlePaperSelectClick}
                    onLowDateChange={this.props.onLowDateChange}
                    onHighDateChange={this.props.onHighDateChange}
                />
            </TextInputBubble>
        )
    }
}

