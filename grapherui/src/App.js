import React, {useState, useEffect} from 'react';
import ReactSlider from 'react-slider';
import Highcharts from 'highcharts'
import HighchartsReact from 'highcharts-react-official'
import './style.css';

function App() {
    return (
        <div className="App">
            <header className="header">
                <div className="mainTitle">
                    <a className="homeLink">The Gallica Grapher</a>
                </div>
            </header>
            <FormBox/>
        </div>
    );
}

class FormBox extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            termInputValue: '',
            paperInputValue: '',
            terms: [],
            papers: [],
            dateBoundary: [1499, 2020],
            currentDateRange: [1499, 2020],
            requestTickets: []
        };
        this.handleChange = this.handleChange.bind(this);
        this.handleClick = this.handleClick.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
        this.handleKeyDown = this.handleKeyDown.bind(this);
        this.deletePaperBubble = this.deletePaperBubble.bind(this);
        this.deleteTermBubble = this.deleteTermBubble.bind(this);
        this.deleteTicket = this.deleteTicket.bind(this);
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
    deleteTicket(ticketBubbleIndex){
        const requestTickets = this.state.requestTickets.slice()
        requestTickets.splice(ticketBubbleIndex, 1)
        this.setState({requestTickets: requestTickets})
    }
    handleClick(paperAndCode){
        const papers = this.state.papers.slice();
        papers.push(paperAndCode)
        this.setState({papers: papers})
    }
    //TODO: make the parameter less confusing. What is getting passed up?
    handleChange(item){
        if(item.length !== 2){
            const target = item.target
            const name = target.name
            if(name === 'papers'){
                this.setState({paperInputValue: target.value})
            }else{
                this.setState({termInputValue: target.value})
            }
        }else{
            this.setState({currentDateRange: item})
        }
    }
    handleKeyDown(event){
        if(event.key === 'Enter'){
            event.preventDefault()
            const terms = this.state.terms.slice();
            terms.push(event.target.value)
            this.setState({terms: terms, termInputValue: ''})
        }
    }
    handleSubmit(event){
        event.preventDefault()
        const requestTickets = this.state.requestTickets.slice()
        const newTicket = {
            'terms': this.state.terms,
            'papersAndCodes': this.state.papers,
            'dateRange': this.state.currentDateRange
        }
        requestTickets.push(newTicket)
        this.setState({
            requestTickets: requestTickets,
            terms: [],
            papers: [],
            currentDateRange: this.state.dateBoundary,
            termInputValue: '',
            paperInputValue: ''
        })

    }
    render() {
        return (
            <div className='formBox'>
                <form onSubmit ={this.handleSubmit} className='itemEntry'>
                    <TermInputBox
                        value={this.state.termInputValue}
                        onChange={this.handleChange}
                        handleKeyDown={this.handleKeyDown}
                        selectedTerms={this.state.terms}
                        deleteTermBubble={this.deleteTermBubble}
                    />
                    <br />
                    {/*To do: lift state up? Handle live search in formbox?
                    Pass handleKeyDown.
                    */}
                    <PaperInputBox
                        onClick={this.handleClick}
                        onChange={this.handleChange}
                        selectedPapers={this.state.papers}
                        deletePaperBubble={this.deletePaperBubble}
                        value={this.state.paperInputValue}
                    />
                    <br />
                    {/*TODO: Add manual entry for dates, can be impractical... input fields?*/}
                    <DateInputBox
                        onChange={this.handleChange}
                        minYear={this.state.dateBoundary[0]}
                        maxYear={this.state.dateBoundary[1]}
                        lowYear={this.state.currentDateRange[0]}
                        highYear={this.state.currentDateRange[1]}
                    />
                    <input
                        type='submit'
                        id='createTicketButton'
                        value='Create Ticket'
                    />
                </form>
                <RequestBox
                    requestTickets={this.state.requestTickets}
                    onClick={this.deleteTicket}
                />
            </div>

        )
    }

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
                onKeyDown={props.handleKeyDown}
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
                    onChange={this.props.onChange}
                />
                <Dropdown
                    papers={this.state.papersForDropdown['paperNameCodes']}
                    error={this.state.dropdownError}
                    onClick={this.props.onClick}
                />
            </div>
        )
    }
}

function Dropdown(props){
    if(props.error){
        return <div>Error: {props.error.message}</div>
    }else if(props.papers){
        return (
            <ul>
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

class DateInputBox extends React.Component{
    constructor(props) {
        super(props);
        this.state = {
            error: null,
            isLoaded: false,
            paperJSON: null
        };
    }
    componentDidMount() {
        fetch("/paperchartjson").then(res => res.json())
            .then(
                (result) => {
                    this.setState({
                        isLoaded: true,
                        paperJSON: result
                    })
                },
                (error) => {
                    this.setState({
                        isLoaded: true,
                        error
                    });
                }
            )
    }
    render() {
        const {error, isLoaded, paperJSON} = this.state;
        if (error) {
            return <div>Error: {error.message}</div>;
        }else if (!isLoaded) {
            return <div>Loading chart...</div>;
        }else{
            const options = {
                chart: {
                    type: 'column',
                    height: '50%'
                },
                title: {
                    text: '# of Publishing Papers by Year'
                },
                yAxis: {
                    title: {
                        text: 'Active newspapers'
                    }
                },
                series: [paperJSON],
                legend: {
                    enabled: false
                }
            }
            return(
                <div>
                    <ReactSlider
                        className="horizontal-slider"
                        thumbClassName="sliderThumb"
                        trackClassName="sliderTrack"
                        value={[this.props.lowYear, this.props.highYear]}
                        max={this.props.maxYear}
                        min={this.props.minYear}
                        pearling
                        onChange={this.props.onChange}
                        ariaLabel={['Lower thumb', 'Upper thumb']}
                        ariaValuetext={state => `Thumb value ${state.valueNow}`}
                        renderThumb={(props, state) => <div {...props}>{state.valueNow}</div>}
                        minDistance={0}

                    />
                    <div className="highchartsContainer">
                        <HighchartsReact
                            highcharts={Highcharts}
                            options={options}
                        />
                    </div>
                </div>
        )
        }
    }
}

function RequestBox(props){
    return(
        <div className='requestBox'>
            <RequestTicketBox
                tickets={props.requestTickets}
                onClick={props.onClick}
            />
            <div className='graphingButtonContainer'>
                <input
                    type='submit'
                    id='startGraphingButton'
                    value='Graph!'
                    onSubmit={props.onSubmit}
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
                    onClick={() => props.onClick(index)}
                    key={index}
                />
            ))}
        </div>
        )
}
function RequestTicket(props){
    return(
        <button
            type="button"
            className='requestBubble'
            onClick={props.onClick}
        >
            <div className="bubbleText">
               <ol>
                <li>{props.ticket['terms'][0]}</li>
                <li>{props.ticket['papersAndCodes'][0]['paper']}</li>
                <li>{props.ticket['dateRange']}</li>
                </ol>
            </div>
        </button>
    );
}

export default App;