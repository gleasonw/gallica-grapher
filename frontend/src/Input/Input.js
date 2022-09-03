import React from "react";
import TicketForm from './TicketForm';
import TicketLabel from "../shared/TicketLabel";
import DecorativeTicket from "../shared/DecorativeTicket";
import ImportantButtonWrap from "../shared/ImportantButtonWrap";

class Input extends React.Component {
    constructor(props) {
        super(props);
        this.exampleBoxRef = React.createRef();
        this.state = {
            terms: [],
            papers: [],
            dateBoundaryPlaceholder: [1499, 2020],
            currentDateRange: ['', ''],
            showNoTicketReminder: false
        };
        this.handleLowDateChange = this.handleLowDateChange.bind(this);
        this.handleHighDateChange = this.handleHighDateChange.bind(this);
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
        const inputLowDate = event.target.value;
        if(this.isNumeric(inputLowDate) || inputLowDate === '') {
            const range = this.state.currentDateRange.slice()
            range[0] = event.target.value
            this.setState({currentDateRange: range})
        }
    }

    handleHighDateChange(event){
        const inputHighDate = event.target.value;
        if(this.isNumeric(inputHighDate) || inputHighDate === '') {
            const range = this.state.currentDateRange.slice()
            range[1] = event.target.value
            this.setState({currentDateRange: range})
        }
    }

    handleKeyDown(event){
        event.preventDefault()
        this.makeTermBubble(event.target.value)
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
            this.setState({terms: terms})
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

    trimDateRangeToPaperBoundary(){
        const range = this.state.currentDateRange.slice()
        const minYear = this.state.dateBoundaryPlaceholder[0]
        const maxYear = this.state.dateBoundaryPlaceholder[1]
        if(range[0] < minYear || range[0] === ''){
            range[0] = minYear
        }
        if(range[1] > maxYear || range[1] === ''){
            range[1] = maxYear
        }
        return range
    }

    isNumeric(str){
        if (typeof str != "string") return false
        return !isNaN(str) && !isNaN(parseFloat(str))
    }

    render() {
        return (
            <div className='inputBody'>
                <div className='inputUI' ref={this.props.formRef}>
                    <div className="mainTitle">
                        Enter a word or phrase to query Gallica then graph the results.
                    </div>
                    <TicketForm
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
                                'dateRange': this.trimDateRangeToPaperBoundary()
                            }
                        )}
                        onPaperDropItemClick={this.handlePaperDropdownClick}
                        onKeyDown={this.handleKeyDown}
                        selectedTerms={this.state.terms}
                        selectedPapers={this.state.papers}
                        deleteTermBubble={this.deleteTermBubble}
                        deletePaperBubble={this.deletePaperBubble}
                        minYearPlaceholder={this.state.dateBoundaryPlaceholder[0]}
                        maxYearPlaceholder={this.state.dateBoundaryPlaceholder[1]}
                        onGraphStartClick={this.props.onInputSubmit}
                        onTicketClick={this.props.onTicketClick}
                        tickets={this.props.requestTickets}
                        exampleBoxRef={this.exampleBoxRef}
                    />
                    <input
                    id='seeExamplesButton'
                    type='button'
                    onClick={this.handleSeeExamplesClick}
                    value='Or try some examples ↓'
                    />
                </div>
            <ExampleBox
                exampleBoxRef={this.exampleBoxRef}
                onExampleRequestClick={this.props.onExampleRequestClick}
            />
            </div>


        )
    }

}
//TODO: Cache the examples.
function ExampleBox(props){
    const exampleJSONdata = require('./exampleRequests.json')
    const exampleRequests = exampleJSONdata["requests"]
    return(
        <div
            className='exampleBox'
            ref={props.exampleBoxRef}
        >
            {Object.keys(exampleRequests).map(requestName => (
                <ExampleRequest
                    title={requestName}
                    request={exampleRequests[requestName]}
                    onClick={props.onExampleRequestClick}
                    key={requestName}
                />
            ))}
        </div>

    )
}
function ExampleRequest(props){
    const tickets = props.request["tickets"]
    return(
        <ImportantButtonWrap onClick={() => props.onClick(tickets)}>
            <h1>{props.title}</h1>
            <div className={'exampleRequest'}>
                {tickets.map((ticket, index) => (
                    <DecorativeTicket key={index}>
                        <TicketLabel
                            terms={ticket["terms"]}
                            papers={ticket["papersAndCodes"]}
                            dateRange={ticket["dateRange"]}
                        />
                    </DecorativeTicket>
                ))}

            </div>
        </ImportantButtonWrap>
    )
}

export default Input;