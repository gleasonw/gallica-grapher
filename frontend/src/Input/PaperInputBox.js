import React from "react";
import TextInputBubble from "./TextInputBubble";
import {SelectionBox} from "./SelectionBox";
import {Dropdown} from "./Dropdown";
import PaperOptionWrap from "./PaperOptionWrap";
import useData from "../shared/hooks/useData";

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

    render() {
        const paperNames = [];
        this.props.selectedPapers.map(paperAndCode => paperNames.push(paperAndCode['title']))
        return (
            <TextInputBubble
                padding={"0"}
            >
                <ContinuousTrendInput
                    lowYear={this.props.lowYear}
                    highYear={this.props.highYear}
                    selected={this.state.selectedInput[0]}
                    onPaperSelectClick={this.handlePaperSelectClick}
                />
                <PaperArrayInput
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
                />
                <FullSearchInput
                    lowYear={this.props.lowYear}
                    highYear={this.props.highYear}
                    selected={this.state.selectedInput[2]}
                    onPaperSelectClick={this.handlePaperSelectClick}
                />
            </TextInputBubble>
        )
    }
}

function ContinuousTrendInput(props) {
    const [limit, setLimit] = React.useState(5000);
    const urlForContinuousPapers =
        "/api/continuousPapers" +
        "?limit=" + limit +
        "&startYear=" + props.lowYear +
        "&endYear=" + props.highYear;
    const result = useData(urlForContinuousPapers);
    let continuousPapers;
    if (result) {
        continuousPapers = result['paperNameCodes'];
    }else{
        continuousPapers = [];
    }
    console.log(continuousPapers)
    return (
        <PaperOptionWrap
            selected={props.selected}
            onClick={() => props.onPaperSelectClick(0)}
        >
            <h5>
                In {continuousPapers.length ? continuousPapers.length : 0} periodicals publishing
                every year between {props.lowYear} and {props.highYear}.
            </h5>
        </PaperOptionWrap>
    )
}

function PaperArrayInput(props) {
    return (
        <PaperOptionWrap
            selected={props.selected}
            onClick={() => props.onPaperSelectClick(1)}
        >
            <SelectionBox
                items={props.paperNames}
                bubblesLabel={'In these periodicals:'}
                onClick={props.deletePaperBubble}
            />
            <input
                type="text"
                value={props.paperInputValue}
                name="papers"
                placeholder="Enter a paper to restrict search..."
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
    const urlForPapersInRange = "/api/numPapersOverRange/" + props.lowYear + "/" + props.highYear;
    const result = useData(urlForPapersInRange);
    let numPapersOverRange;
    if (result) {
        numPapersOverRange = result['numPapersOverRange'];
    }else{
        numPapersOverRange = "...";
    }
    return (
        <PaperOptionWrap
            selected={props.selected}
            borderBottom={'none'}
            onClick={() => props.onPaperSelectClick(2)}
        >
            <h5>
                In {numPapersOverRange} periodicals publishing
                at any point between {props.lowYear} and {props.highYear}.
            </h5>
        </PaperOptionWrap>
    )
}