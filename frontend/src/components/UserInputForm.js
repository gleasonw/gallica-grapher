import React, {useState} from 'react';
import TicketLabel from "./TicketLabel";

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
        if (props.tickets && props.tickets.length > 0){
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
                onChange={props.onTermChange}
                onKeyDown={props.onKeyDown}
                selectedTerms={props.selectedTerms}
                deleteTermBubble={props.deleteTermBubble}
            />
            <br />
            <PaperInputBox
                onClick={props.onPaperDropItemClick}
                onChange={props.onPaperChange}
                selectedPapers={props.selectedPapers}
                deletePaperBubble={props.deletePaperBubble}
            />
            <br />
            <DateInputBox
                onLowDateChange={props.onLowDateChange}
                onHighDateChange={props.onHighDateChange}
                minYearPlaceholder={props.minYearPlaceholder}
                maxYearPlaceholder={props.maxYearPlaceholder}
                lowYear={props.lowYearValue}
                highYear={props.highYearValue}
            />
            <div className='graphWarningBoxBoundary'>
                {showTicketReminder && props.tickets.length === 0 ? noTicketReminder : null}
                <div className='createTicketAndGraphButtonContainer'>
                    <input
                        type='button'
                        id='createTicketButton'
                        value='Add series +'
                        onClick={handleCreateTicketClick}
                    />
                    <input
                        type='submit'
                        id='graphButton'
                        value='Fetch and graph 📊'
                    />
                </div>
                <RequestBox
                    tickets={props.tickets}
                    onTicketClick={props.onTicketClick}
                />
            </div>


        </form>
    )
}
function TermInputBox(props){
    const [termInput, setTermInput] = useState('');

    function handleTermChange(event){
        setTermInput(event.target.value)
    }

    function handleKeyDown(event){
        if(event.key === 'Enter'){
            props.onKeyDown(event);
            setTermInput('');
        }
    }

    return(
        <div className='inputContainer'>
            <SelectionBox
                items={props.selectedTerms}
                bubblesLabel={'Terms:'}
                onClick={props.deleteTermBubble}
            />
            <input
                type="text"
                value={termInput}
                name="terms"
                placeholder="Enter a term..."
                onChange={handleTermChange}
                onKeyDown={handleKeyDown}
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
            paperInputValue: '',
        }
        this.handleKeyUp = this.handleKeyUp.bind(this);
        this.handleDropdownClick = this.handleDropdownClick.bind(this);
        this.handlePaperChange = this.handlePaperChange.bind(this);
    }

    handlePaperChange(event){
        this.setState({paperInputValue: event.target.value})
    }

    handleKeyUp(event){
        clearTimeout(this.state.timerForSpacingAjaxRequests);
        if (event.target.value){
            this.setState({
                timerForSpacingAjaxRequests:
                setTimeout(() => {this.getPaperDropdownItems(event.target.value)}, 500)
                }
            );
        }else{
            this.setState({
                papersForDropdown: [],
            })
        }
    }

    getPaperDropdownItems(searchString){
        fetch("/api/papers/" + searchString)
            .then(res => res.json())
            .then(
                (result) => {
                    console.log(result);
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

    handleDropdownClick(paperNameCode){
        this.props.onClick(paperNameCode);
        this.setState({
            papersForDropdown: [],
            paperInputValue: '',
        })
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
                        value={this.state.paperInputValue}
                        name="papers"
                        placeholder="Search for a paper to restrict search..."
                        onKeyUp={this.handleKeyUp}
                        onChange={this.handlePaperChange}
                        autoComplete="off"
                    />
                </div>
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

function RequestBox(props){
    return(
        <div className={'requestBoxContainer'}>
            <div className='requestBox'>
                <RequestTicketBox
                    tickets={props.tickets}
                    onTicketClick={props.onTicketClick}
                />
            </div>
        </div>
    );

}
function RequestTicketBox(props){
    if(props.tickets && props.tickets.length > 0){
        return(
            <div className="ticketBubbleContainer">
                {props.tickets.map((ticket, index) => (
                    <RequestTicket
                        ticket={ticket}
                        onClick={() => props.onTicketClick(index)}
                        key={index}
                    />
                ))}
            </div>
            )
    }else{
        return(
            <div className="ticketBubbleContainer">
                <div id='placeHolderTicket'/>
            </div>
        )
    }
}
function RequestTicket(props){
    const terms = props.ticket['terms']
    const papers = props.ticket['papersAndCodes']
    const dateRange = props.ticket['dateRange']
    return(
        <button
            type="button"
            className='requestBubble'
            onClick={props.onClick}
        >
            <div className="ticket">
                <TicketLabel
                    terms={terms}
                    papers={papers}
                    dateRange={dateRange}
                />
            </div>
        </button>
    );
}

export default UserInputForm;