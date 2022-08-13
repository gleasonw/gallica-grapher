import React from "react";
import UserInputForm from './UserInputForm';
import TicketLabel from "./TicketLabel";

class InputUI extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            termInputValue: '',
            paperInputValue: '',
            terms: [],
            papers: [],
            dateBoundary: [1499, 2020],
            currentDateRange: ['', ''],
            showNoTicketReminder: false
        };
        this.handleLowDateChange = this.handleLowDateChange.bind(this);
        this.handleHighDateChange = this.handleHighDateChange.bind(this);
        this.handlePaperChange = this.handlePaperChange.bind(this);
        this.handleTermChange = this.handleTermChange.bind(this);
        this.handleClick = this.handleClick.bind(this);
        this.handleKeyDown = this.handleKeyDown.bind(this);
        this.deletePaperBubble = this.deletePaperBubble.bind(this);
        this.deleteTermBubble = this.deleteTermBubble.bind(this);
    }
    deletePaperBubble(bubbleIndex){
        const papers = this.state.papers.slice()
        papers.splice(bubbleIndex, 1)
        this.setState({papers: papers})
    }
    deleteTermBubble(bubbleIndex){
        const terms = this.state.terms.slice()
        terms.splice(bubbleIndex, 1)
        this.setState({terms: terms})
    }
    handleClick(paperAndCode){
        this.makePaperBubble(paperAndCode)
    }
    handleLowDateChange(event){
        const range = this.state.currentDateRange.slice()
        range[0] = event.target.value
        this.setState({currentDateRange: range})
    }
    handleHighDateChange(event){
        const range = this.state.currentDateRange.slice()
        range[1] = event.target.value
        this.setState({currentDateRange: range})
    }
    handlePaperChange(event){
        this.setState({paperInputValue: event.target.value})
    }
    handleTermChange(event){
        this.setState({termInputValue: event.target.value})
    }
    handleKeyDown(event){
        if(event.key === 'Enter'){
            event.preventDefault()
            if(event.target.name === 'terms'){
                this.makeTermBubble(event.target.value)
            }
        }
    }
    makePaperBubble(paperAndCode){
        const papers = this.state.papers.slice();
        papers.push(paperAndCode)
        this.setState({papers: papers})
    }
    makeTermBubble(term){
        if(term){
            const terms = this.state.terms.slice();
            terms.push(term)
            this.setState({terms: terms, termInputValue: ''})
        }
    }
    render() {
        return (
            <div className='inputBody'>
                <div className='inputFormAndRequestBoxContainer'>
                    <div className='inputUI'>
                        {this.props.header}
                        <div className="mainTitle">
                            Enter a word or phrase to query Gallica then graph the results.
                        </div>
                        <UserInputForm
                            termInputValue={this.state.termInputValue}
                            paperInputValue={this.state.paperInputValue}
                            lowYearValue={this.state.currentDateRange[0]}
                            highYearValue={this.state.currentDateRange[1]}
                            onLowDateChange={this.handleLowDateChange}
                            onHighDateChange={this.handleHighDateChange}
                            onPaperChange={this.handlePaperChange}
                            onTermChange={this.handleTermChange}
                            onCreateTicketClick={() => this.props.onCreateTicketClick(
                                {
                                    'terms': this.state.terms,
                                    'papersAndCodes': this.state.papers,
                                    'dateRange':
                                        this.state.currentDateRange[0] &&
                                        this.state.currentDateRange[1] ?
                                            this.state.currentDateRange :
                                            [1499, 2020]
                                }
                            )}
                            onPaperDropItemClick={this.handleClick}
                            onKeyDown={this.handleKeyDown}
                            selectedTerms={this.state.terms}
                            selectedPapers={this.state.papers}
                            deleteTermBubble={this.deleteTermBubble}
                            deletePaperBubble={this.deletePaperBubble}
                            minYear={this.state.dateBoundary[0]}
                            maxYear={this.state.dateBoundary[1]}
                            onGraphStartClick={this.props.onInputSubmit}
                            thereAreTickets={this.props.thereAreTickets}
                        />
                        <RequestBox
                            requestTickets={this.props.requestTickets}
                            onTicketClick={this.props.onTicketClick}
                        />
                    </div>
                    <div className='seeExamplesButton'>
                        <div className='seeExamplesText'>
                            Try example queries ↓
                        </div>
                    </div>
                </div>
            <ExampleBox/>
            </div>


        )
    }

}
function ExampleBox(props){
    return(
        <div className='exampleBox'>
            Or, try an example.
            <ExampleQuery
                terms={['Jules Verne']}
                papers={[{'paper': 'Le Livre de la jungle', 'code': 'LJN'}]}
                dateRange={['1850', '1860']}
            />
            <ExampleQuery
                terms={['Jules Verne']}
                papers={[{'paper': 'Le Livre de la jungle', 'code': 'LJN'}]}
                dateRange={['1850', '1860']}
            />
        </div>

    )
}
function ExampleQuery(props){
    return(
        <div className='exampleQuery'>
            <TicketLabel
                terms={props.terms}
                papers={props.papers}
                dateRange={props.dateRange}
            />
        </div>
    )
}
function RequestBox(props){
    return(
        <div className='requestBox'>
            <div className='requestTicketsContainer'>
                <RequestTicketBox
                    tickets={props.requestTickets}
                    onTicketClick={props.onTicketClick}
                />
            </div>
        </div>
    );

}
function RequestTicketBox(props){
    return(
        <div className="ticketBox">
            {props.tickets.map((ticket, index) => (
                <RequestTicket
                    ticket={ticket}
                    onClick={() => props.onTicketClick(index)}
                    key={index}
                />
            ))}
        </div>
        )
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

export default InputUI;