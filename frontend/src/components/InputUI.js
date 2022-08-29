import React from "react";
import UserInputForm from './UserInputForm';
import TicketLabel from "./TicketLabel";

class InputUI extends React.Component {
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
        const range = this.state.currentDateRange.slice()
        range[0] = event.target.value
        this.setState({currentDateRange: range})
    }

    handleHighDateChange(event){
        const range = this.state.currentDateRange.slice()
        range[1] = event.target.value
        this.setState({currentDateRange: range})
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

    render() {
        return (
            <div className='inputBody'>
                <div className='inputUI' ref={this.props.formRef}>
                    <div className="mainTitle">
                        Enter a word or phrase to query Gallica then graph the results.
                    </div>
                    <UserInputForm
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
                formRef={this.props.formRef}
                onExampleRequestClick={this.props.onExampleRequestClick}
            />
            </div>


        )
    }

}
//TODO: Cache the examples.
function ExampleBox(props){
    const exampleRequests = [
        [
            {"terms":["chicago"],"papersAndCodes":[{"code":"cb32895690j","endDate":1944,"startDate":1863,"title":"Le Petit journal (Paris. 1863)"}],"dateRange":["1863","1944"]},
            {"terms":["new york"],"papersAndCodes":[{"code":"cb32895690j","endDate":1944,"startDate":1863,"title":"Le Petit journal (Paris. 1863)"}],"dateRange":["1863","1944"]},
            {"terms":["londres"],"papersAndCodes":[{"code":"cb32895690j","endDate":1944,"startDate":1863,"title":"Le Petit journal (Paris. 1863)"}],"dateRange":["1863","1944"]}
        ],
        [
            {"terms":["boeuf"],"papersAndCodes":[{"code":"cb344287435","endDate":1925,"startDate":1883,"title":"L'Art culinaire (Société des cuisiniers français)"}],"dateRange":["1883","1925"]}
        ],
        [
            {"terms":["colonies","algerie","congo","conquete"],"papersAndCodes":[{"code":"cb32757974m","endDate":1921,"startDate":1871,"title":"Le XIXe siècle (Paris. 1871)"},{"code":"cb328066631","endDate":1940,"startDate":1865,"title":"La Liberté"},{"code":"cb328123058","endDate":1944,"startDate":1884,"title":"Le Matin (Paris. 1884)"},{"code":"cb34355551z","endDate":1951,"startDate":1854,"title":"Le Figaro (Paris. 1854)"},{"code":"cb32895690j","endDate":1944,"startDate":1863,"title":"Le Petit journal (Paris. 1863)"}],"dateRange":[1499,2020]}
        ],
        [
            {"terms":["guerre","souffrance","sang"],"papersAndCodes":[{"code":"cb32757974m","endDate":1921,"startDate":1871,"title":"Le XIXe siècle (Paris. 1871)"}],"dateRange":["1871","1921"]},
            {"terms":["paix","accord","amitie"],"papersAndCodes":[{"code":"cb32757974m","endDate":1921,"startDate":1871,"title":"Le XIXe siècle (Paris. 1871)"}],"dateRange":["1871","1921"]}
        ]
    ]
    return(
        <div
            className='exampleBox'
            ref={props.exampleBoxRef}
        >
            <div className='exampleRequestsContainer'>
                {exampleRequests.map((request, index) => (
                    <ExampleRequest
                        request={request}
                        onClick={() => props.onExampleRequestClick(request)}
                        key={index}
                    />
                ))}
            </div>

        </div>

    )
}
function ExampleRequest(props){
    return(
        <div
            className='exampleRequest'
            onClick={() => props.onClick(props.request)}
        >
            {props.request.map((ticket, index) => (
                <div
                    className='exampleTicket'
                    key={index}
                >
                    <TicketLabel
                        terms={ticket["terms"]}
                        papers={ticket["papersAndCodes"]}
                        dateRange={ticket["dateRange"]}
                    />
                </div>
            ))}
        </div>
    )
}

export default InputUI;