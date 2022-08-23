import React, {useRef} from "react";
import UserInputForm from './UserInputForm';
import TicketLabel from "./TicketLabel";

class InputUI extends React.Component {
    constructor(props) {
        super(props);
        this.exampleBoxRef = React.createRef();
        this.state = {
            termInputValue: '',
            paperInputValue: '',
            terms: [],
            papers: [],
            dateBoundary: [1499, 2020],
            dateBoundaryPlaceholder: [1499, 2020],
            currentDateRange: ['', ''],
            showNoTicketReminder: false
        };
        this.handleLowDateChange = this.handleLowDateChange.bind(this);
        this.handleHighDateChange = this.handleHighDateChange.bind(this);
        this.handlePaperChange = this.handlePaperChange.bind(this);
        this.handleTermChange = this.handleTermChange.bind(this);
        this.handlePaperDropdownClick = this.handlePaperDropdownClick.bind(this);
        this.handleKeyDown = this.handleKeyDown.bind(this);
        this.handleSeeExamplesClick = this.handleSeeExamplesClick.bind(this);
        this.deletePaperBubble = this.deletePaperBubble.bind(this);
        this.deleteTermBubble = this.deleteTermBubble.bind(this);
    }
    deletePaperBubble(bubbleIndex){
        const papers = this.state.papers.slice()
        papers.splice(bubbleIndex, 1)
        this.updateDateBoundaryPlaceholder(papers)
        this.setState({papers: papers})
    }
    deleteTermBubble(bubbleIndex){
        const terms = this.state.terms.slice()
        terms.splice(bubbleIndex, 1)
        this.setState({terms: terms})
    }
    handlePaperDropdownClick(paper){
        this.makePaperBubble(paper)
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
    handleSeeExamplesClick(){
        this.exampleBoxRef.current.scrollIntoView({behavior: "smooth"})
    }
    makePaperBubble(paper){
        const papers = this.state.papers.slice();
        papers.push(paper)
        this.updateDateBoundaryPlaceholder(papers)
        this.setState({papers: papers})
    }

    makeTermBubble(term){
        if(term){
            const terms = this.state.terms.slice();
            terms.push(term)
            this.setState({terms: terms, termInputValue: ''})
        }
    }

    updateDateBoundaryPlaceholder(papers){
        let minYear = 1499
        let maxYear = 2020
        if(papers.length > 0){
            const paperLowYears = papers.map(paper => paper["startDate"])
            const paperHighYears = papers.map(paper => paper["endDate"])
            minYear = Math.min(...paperLowYears)
            maxYear = Math.max(...paperHighYears)
        }
        console.log(minYear, maxYear)
        this.setState({dateBoundaryPlaceholder: [minYear, maxYear]})
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
                            onPaperDropItemClick={this.handlePaperDropdownClick}
                            onKeyDown={this.handleKeyDown}
                            selectedTerms={this.state.terms}
                            selectedPapers={this.state.papers}
                            deleteTermBubble={this.deleteTermBubble}
                            deletePaperBubble={this.deletePaperBubble}
                            minYear={this.state.dateBoundary[0]}
                            maxYear={this.state.dateBoundary[1]}
                            minYearPlaceholder={this.state.dateBoundaryPlaceholder[0]}
                            maxYearPlaceholder={this.state.dateBoundaryPlaceholder[1]}
                            onGraphStartClick={this.props.onInputSubmit}
                            thereAreTickets={this.props.thereAreTickets}
                        />
                        <RequestBox
                            requestTickets={this.props.requestTickets}
                            onTicketClick={this.props.onTicketClick}
                            thereAreTickets={this.props.thereAreTickets}
                        />
                        <input
                        id='seeExamplesButton'
                        type='button'
                        onClick={this.handleSeeExamplesClick}
                        value='Try example queries ↓'
                        />
                    </div>
                </div>
            <ExampleBox exampleBoxRef={this.exampleBoxRef}/>
            </div>


        )
    }

}
function ExampleBox(props){
    return(
        <div
            className='exampleBox'
            ref={props.exampleBoxRef}
        >
            <div className='exampleRequestsContainer'>
                <ExampleRequest
                    terms={['Jules Verne']}
                    papers={[{'paper': 'Le Livre de la jungle', 'code': 'LJN'}]}
                    dateRange={['1850', '1860']}
                />
                <ExampleRequest
                    terms={['Jules Verne']}
                    papers={[{'paper': 'Le Livre de la jungle', 'code': 'LJN'}]}
                    dateRange={['1850', '1860']}
                />
            </div>

        </div>

    )
}
function ExampleRequest(props){
    return(
        <div className='exampleRequest'>
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
        <div className={'requestBoxContainer'}>
            <div className='requestBox'>
                <span className={'requestBoxLabel'}>Tickets</span>
                <div className='requestTicketsContainer'>
                    <RequestTicketBox
                        tickets={props.requestTickets}
                        onTicketClick={props.onTicketClick}
                        thereAreTickets={props.thereAreTickets}
                    />
                </div>
            </div>
        </div>
    );

}
function RequestTicketBox(props){
    if(props.thereAreTickets){
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
    }else{
        return(
            <div className="ticketBox">
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

export default InputUI;