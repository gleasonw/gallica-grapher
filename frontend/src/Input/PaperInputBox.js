import React from "react";
import TextInputBubble from "./TextInputBubble";
import {SelectionBox} from "./SelectionBox";
import {Dropdown} from "./Dropdown";

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
                    console.log(result);
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
        const paperNames = [];
        this.props.selectedPapers.map(paperAndCode => paperNames.push(paperAndCode['title']))
        return (
            <div>
                <TextInputBubble>
                    <SelectionBox
                        items={paperNames}
                        bubblesLabel={'In paper(s):'}
                        onClick={this.props.deletePaperBubble}
                    />
                    <input
                        type="text"
                        value={this.state.paperInputValue}
                        name="papers"
                        placeholder="Search for a paper to restrict search..."
                        onKeyUp={this.handleKeyUp}
                        onChange={this.handlePaperChange}
                        autoComplete="off"
                    />
                </TextInputBubble>
                <div className='dropdownContainer'>
                    <Dropdown
                        papers={this.state.papersForDropdown['paperNameCodes']}
                        error={this.state.dropdownError}
                        onClick={this.handleDropdownClick}
                    />
                </div>
            </div>
        )
    }
}