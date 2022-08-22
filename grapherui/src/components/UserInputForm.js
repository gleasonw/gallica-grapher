import React, {useState} from 'react';

function UserInputForm(props){
    const [showTicketReminder, setShowTicketReminder] = useState(false);
    const noTicketReminder =
        <div>
            <div className='noTicketReminder'>
                <span className='noTicketReminderText'>
                    You have no tickets.
                </span>
            </div>
        </div>

    function handleSubmit(e){
        e.preventDefault();
        if (props.thereAreTickets){
            props.onGraphStartClick(e);
        }else{
            setShowTicketReminder(true);
        }
    }

    function handleCreateTicketClick(){
        setShowTicketReminder(false);
        props.onCreateTicketClick();
    }

    return(
        <form
            onSubmit={handleSubmit}
            className='userInputForm'
        >
            <TermInputBox
                value={props.termInputValue}
                onChange={props.onTermChange}
                onKeyDown={props.onKeyDown}
                selectedTerms={props.selectedTerms}
                deleteTermBubble={props.deleteTermBubble}
            />
            <br />
            <PaperInputBox
                onClick={props.onPaperDropItemClick}
                onChange={props.onPaperChange}
                onKeyDown={props.onKeyDown}
                selectedPapers={props.selectedPapers}
                deletePaperBubble={props.deletePaperBubble}
                value={props.paperInputValue}
            />
            <br />
            <DateInputBox
                onLowDateChange={props.onLowDateChange}
                onHighDateChange={props.onHighDateChange}
                minYear={props.minYear}
                maxYear={props.maxYear}
                minYearPlaceholder={props.minYearPlaceholder}
                maxYearPlaceholder={props.maxYearPlaceholder}
                lowYear={props.lowYearValue}
                highYear={props.highYearValue}
            />
            <div className='graphWarningBoxBoundary'>
                {showTicketReminder && !props.thereAreTickets ? noTicketReminder : null}
                <div className='createTicketAndGraphButtonContainer'>
                    <input
                        type='submit'
                        id='graphButton'
                        value='Graph 📊'
                    />
                    <input
                        type='button'
                        id='createTicketButton'
                        value='Add query +'
                        onClick={handleCreateTicketClick}
                    />
                </div>
            </div>


        </form>
    )
}
function TermInputBox(props){
    return(
        <div className='inputContainer'>
            <SelectionBox
                items={props.selectedTerms}
                bubblesLabel={'Terms:'}
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
        this.props.selectedPapers.map(paperAndCode => paperNames.push(paperAndCode['title']))
        return(
            <div>
                <div className='inputContainer'>
                    <SelectionBox
                        items={paperNames}
                        bubblesLabel={'In Papers:'}
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
                {props.papers.map(paper => (
                    <DropdownItem
                        key={paper['code']}
                        paper={paper['title']}
                        onClick={() => props.onClick(paper)}
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
            <span className='bubbleText'>
                {props.item}
            </span>
            <div className='bubbleDeleteButton'>
                <svg className="deleteButton" xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">
                    <g transform="rotate(-45 50 50)">
                        <rect x="0" y="40" width="100" height="20"></rect>
                    </g>
                    <g transform="rotate(45 50 50)">
                        <rect x="0" y="40" width="100" height="20"></rect>
                    </g>
                </svg>
            </div>
        </button>
    )
}

function SelectionBox(props){
        return(
        <div className='bubblesContainer'>
            <span className='bubblesLabel'>
                {props.bubblesLabel}
            </span>
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
            <div className='inputContainer'>
            <input
                id="lowYear"
                type='text'
                value={props.lowYear}
                onChange={props.onLowDateChange}
                placeholder={props.minYearPlaceholder}
            />
            </div>
            to
            <div className='inputContainer'>
            <input
                id="highYear"
                type='text'
                value={props.highYear}
                onChange={props.onHighDateChange}
                placeholder={props.maxYearPlaceholder}
            />
            </div>
        </div>
    )
}

export default UserInputForm;