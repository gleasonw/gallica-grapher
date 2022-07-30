import React from 'react';
import TextField from "@mui/material/TextField";

function UserInputForm(props){
    return(
        <form onSubmit={props.onSubmit} className='userInputForm'>
            <TermInputBox
                value={props.termInputValue}
                onChange={props.onChange}
                onKeyDown={props.onKeyDown}
                selectedTerms={props.selectedTerms}
                deleteTermBubble={props.deleteTermBubble}
            />
            <br />
            <PaperInputBox
                onClick={props.onPaperDropItemClick}
                onChange={props.onChange}
                onKeyDown={props.onKeyDown}
                selectedPapers={props.selectedPapers}
                deletePaperBubble={props.deletePaperBubble}
                value={props.paperInputValue}
            />
            <br />
            <DateInputBox
                onChange={props.onChange}
                minYear={props.minYear}
                maxYear={props.maxYear}
                lowYear={props.lowYearValue}
                highYear={props.highYearValue}
            />
        </form>
    )
}
function TermInputBox(props){
    return(
        <div className='inputContainer'>
            <SelectionBox
                items={props.selectedTerms}
                onClick={props.deleteTermBubble}
            />
            <input
                type="text"
                value={props.value}
                name="terms"
                placeholder="Enter a term..."
                onChange={props.onChange}
                onKeyDown={props.onKeyDown}
                autoComplete="off"
            />
        </div>
    )
}

class PaperInputBox extends React.Component{
    constructor(props){
        super(props);
        this.state = {
            timerForSpacingAjaxRequests: null,
            papersForDropdown:[],
            dropdownError: null,
        }
        this.handleKeyUp = this.handleKeyUp.bind(this);
    }
    handleKeyUp(event){
        clearTimeout(this.state.timerForSpacingAjaxRequests);
        if (event.target.value){
            this.setState({
                timerForSpacingAjaxRequests:
                setTimeout(() => {this.getPaperDropdownItems(event.target.value)}, 1000)
                }
            );
        }else{
            this.setState({
                papersForDropdown: [],
            })
        }
    }
    getPaperDropdownItems(searchString){
        fetch("/papers/" + searchString)
            .then(res => res.json())
            .then(
                (result) => {
                    this.setState({
                        papersForDropdown: result});
                },
                (dropdownError) => {
                    this.setState({
                        dropdownError
                    })

                }
            )
    }
    render() {
        const paperNames = [];
        this.props.selectedPapers.map(paperAndCode => paperNames.push(paperAndCode['paper']))
        return(
            <div>
                <div className='inputContainer'>
                    <SelectionBox
                        items={paperNames}
                        onClick={this.props.deletePaperBubble}
                    />
                    <input
                        type="text"
                        value={this.props.paperInputValue}
                        name="papers"
                        placeholder="Search for a paper to restrict search..."
                        onKeyUp={this.handleKeyUp}
                        onKeyDown={this.props.onKeyDown}
                        onChange={this.props.onChange}
                        autoComplete="off"
                    />
                </div>
                <div className='dropdownContainer'>
                    <Dropdown
                        papers={this.state.papersForDropdown['paperNameCodes']}
                        error={this.state.dropdownError}
                        onClick={this.props.onClick}
                    />
                </div>
            </div>
        )
    }
}

function Dropdown(props){
    if(props.error){
        return <div>Error: {props.error.message}</div>
    }else if(props.papers){
        return (
            <ul className='paperDropdown'>
                {props.papers.map(paperAndCode => (
                    <DropdownItem
                        key={paperAndCode['code']}
                        paper={paperAndCode['paper']}
                        onClick={() => props.onClick(paperAndCode)}
                    />
                ))}
            </ul>
        );
    }else{
        return(<div/>)
    }
}

function DropdownItem(props){
    return(
        <button
            type="button"
            className='paperDropdownItem'
            onClick={props.onClick}
        >
            {props.paper}
        </button>
    )
}

function SelectionBubble(props){
    return(
        <button
            className='bubbleItem'
            type='button'
            onClick={props.onClick}
        >
            <div className='bubbleText'>
                {props.item}
            </div>
        </button>
    )
}

function SelectionBox(props){
        return(
        <div className='bubblesContainer'>
            {props.items.map((item,index) => (
            <SelectionBubble
                onClick={() => props.onClick(index)}
                key={index}
                item={item}
            />
            ))}
        </div>
        )
}

function DateInputBox(props){
    return(
        <div className='dateInputs'>
            <TextField
                id="lowYear"
                label="Low Year"
                value={props.lowYear}
                onChange={props.onChange}
            sx={{
                color: 'white',
            }}/>
            to
            <TextField
                id="highYear"
                label="High Year"
                value={props.highYear}
                onChange={props.onChange} />
        </div>
    )
}

export default UserInputForm;