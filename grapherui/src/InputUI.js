import React from "react";
import UserInputForm from './UserInputForm';
import TicketInfo from "./TicketInfo";

class InputUI extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            termInputValue: '',
            paperInputValue: '',
            terms: [],
            papers: [],
            dateBoundary: [1499, 2020],
            currentDateRange: [1499, 2020],
        };
        this.handleChange = this.handleChange.bind(this);
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
    handleChange(item){
        if(item.length !== 2){
            this.updateInputValue(item)
        }else{
            this.setState({currentDateRange: item})
        }
    }
    handleKeyDown(event){
        if(event.key === 'Enter'){
            event.preventDefault()
            if(event.target.name === 'terms'){
                this.makeTermBubble(event.target.value)
            }
        }
    }
    updateInputValue(event){
        const target = event.target
            const name = target.name
            if(name === 'papers'){
                this.setState({paperInputValue: target.value})
            }else{
                this.setState({termInputValue: target.value})
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
            <div className='inputUI'>
                <UserInputForm
                    termInputValue={this.state.termInputValue}
                    paperInputValue={this.state.paperInputValue}
                    lowYearValue={this.state.currentDateRange[0]}
                    highYearValue={this.state.currentDateRange[1]}
                    onChange={this.handleChange}
                    onClick={() => this.props.onCreateTicketClick(
                        {
                            'terms': this.state.terms,
                            'papersAndCodes': this.state.papers,
                            'dateRange': this.state.currentDateRange
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
                />
                <RequestBox
                    requestTickets={this.props.requestTickets}
                    onTicketClick={this.props.onTicketClick}
                    onGraphStartClick={this.props.onInputSubmit}
                />
            </div>

        )
    }

}
function RequestBox(props){
    return(
        <div className='requestBox'>
            <RequestTicketBox
                tickets={props.requestTickets}
                onTicketClick={props.onTicketClick}
            />
            <div className='graphingButtonContainer'>
                <input
                    type='submit'
                    id='startGraphingButton'
                    value='Graph!'
                    onClick={props.onGraphStartClick}
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
                <TicketInfo
                    terms={terms}
                    papers={papers}
                    dateRange={dateRange}
                />
            </div>
        </button>
    );
}

export default InputUI;