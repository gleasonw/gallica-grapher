import React from "react";
import TextInputBubble from "./TextInputBubble";
import {SelectionBox} from "./SelectionBox";
import {Dropdown} from "./Dropdown";
import PaperOptionWrap from "./PaperOptionWrap";

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
            <TextInputBubble>
                <ContinuousTrendInput/>
                <PaperArrayInput
                    paperNames={paperNames}
                    deletePaperBubble={this.props.deletePaperBubble}
                    paperInputValue={this.state.paperInputValue}
                    onKeyUp={this.handleKeyUp}
                    onChange={this.handlePaperChange}
                    papersForDropdown={this.state.papersForDropdown}
                    onClick={this.handleDropdownClick}
                    error={this.state.dropdownError}
                    onDropdownClick={this.handleDropdownClick}
                />
                <FullSearchInput/>
            </TextInputBubble>
        )
    }
}

function ContinuousTrendInput(props) {
    return (
        <PaperOptionWrap>
            <input
                type='checkbox'
                name='continuousTrend'
                id='continuousTrend'
            />
            <label htmlFor='continuousTrend'>Continuous trend</label>
        </PaperOptionWrap>
    )
}

function PaperArrayInput(props) {
    return (
        <PaperOptionWrap>
            <SelectionBox
                items={props.paperNames}
                bubblesLabel={'In paper(s):'}
                onClick={props.deletePaperBubble}
            />
            <input
                type="text"
                value={props.paperInputValue}
                name="papers"
                placeholder="Search for a paper to restrict search..."
                onKeyUp={props.onKeyUp}
                onChange={props.onPaperChange}
                autoComplete="off"
            />
            <div className='dropdownContainer'>
                <Dropdown
                    papers={props.papersForDropdown['paperNameCodes']}
                    error={props.dropdownError}
                    onClick={props.onDropdownClick}
                />
            </div>
        </PaperOptionWrap>

    )
}

function FullSearchInput(props) {
    return (
        <PaperOptionWrap>
            <input
                type='checkbox'
                name='fullSearch'
                id='fullSearch'
            />
            <label htmlFor='fullSearch'>Full search</label>
        </PaperOptionWrap>
    )
}