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
            paperNames: [],
            paperCodes: [],
            dateBoundary: [1499, 2020],
            currentDateRange: [1499, 2020],
            requestTickets: [],
        };
        this.handleChange = this.handleChange.bind(this);
        this.handleClick = this.handleClick.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
        this.handleKeyDown = this.handleKeyDown.bind(this);
    }
    deleteBubble(item, isPaper){

    }
    handleClick(paperAndCode){
        let paper = paperAndCode['paper']
        let code = paperAndCode['code']
        const paperNames = this.state.paperNames.slice();
        paperNames.push(paper)
        const paperCodes = this.state.paperCodes.slice();
        paperCodes.push(code)
        this.setState({paperNames: paperNames, paperCodes: paperCodes})
    }
    //TODO: make the parameter less confusing. What is getting passed up?
    handleChange(item){
        if(item.length !== 2){
            const target = item.target
            const name = target.name
            if(name === 'papers'){
                this.setState({paperInputValue: target.value})
            }else{
                this.setState({textInputValue: target.value})
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
            this.setState({terms: terms, textValue: ''})
        }
    }
    handleSubmit(event){
        event.preventDefault()
        console.log(this.state.terms)
        console.log(this.state.paperNames)
        console.log(this.state.currentDateRange)
    }
    render() {
        return (
            <div className='formBox'>
                <form onSubmit ={this.handleSubmit} className='itemEntry'>
                    <TermInputBox
                        value={this.state.textInputValue}
                        onChange={this.handleChange}
                        handleKeyDown={this.handleKeyDown}
                        selectedTerms={this.state.terms}
                        deleteTermBubble={this.deleteBubble}
                    />
                    <br />
                    {/*To do: lift state up? Handle live search in formbox?
                    Pass handleKeyDown.
                    */}
                    <PaperInputBox
                        onClick={this.handleClick}
                        onChange={this.handleChange}
                        selectedPapers={this.state.paperNames}
                        deletePaperBubble={this.deleteBubble}
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
                <RequestBox/>
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
            paperOptions: []
        }
        this.handleKeyUp = this.handleKeyUp.bind(this);
    }
    handleKeyUp(event){
        clearTimeout(this.state.timerForSpacingAjaxRequests);
        if (event.target.value){
            this.setState({
                timerForSpacingAjaxRequests:
                setTimeout(() => {this.getPaperDropdownItems(event.target.value)}, 1500)
                }
            );
        }
    }
    getPaperDropdownItems(searchString){
        let errorThrown = null;
        let isLoaded = false;
        fetch("/papers/" + searchString)
            .then(res => res.json())
            .then(
                (result) => {
                    isLoaded = true;
                    this.setState({paperOptions: result});
                },
                (error) => {
                    isLoaded = true;
                    errorThrown = error
                }
            )
        if (errorThrown) {
            this.setState({paperOptions: [<div>Error: {errorThrown.message}</div>]});
        }if (!isLoaded) {
            this.setState({paperOptions: [<div>Loading...</div>]});
        }
    }
    render() {
        return(
            <div className='inputContainer'>
                <SelectionBox
                    items={this.props.selectedPapers}
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
                    paperOptions={this.state.paperOptions}
                    onClick={this.props.onClick}
                />
            </div>
        )
    }
}

function Dropdown(props){
    let papers = props.paperOptions['paperNameCodes']
    if(papers){
        return (
            <ul>
                {papers.map(paperAndCode => (
                    <li key={paperAndCode['code']}>
                        <button
                            type='button'
                            onClick={() => props.onClick(paperAndCode)}
                        >
                            {paperAndCode['paper']}
                        </button>
                    </li>
                ))}
            </ul>
        );
    }else{
        return(
            <div>{papers}</div>
        )
    }
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
            return <div>Loading...</div>;
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

//TODO: Catch duplicate key error, pass
function SelectionBox(props){
    return(
        <div className='bubblesContainer'>
            {props.items.map(item => (
            <button
                className='bubbleItem'
                type='button'
                onClick={() => props.onClick(item)}
                key={item}
            >
                <div className='bubbleText'>
                    {item}
                </div>
            </button>
        ))}
        </div>
    )
}

class RequestBox extends React.Component {
    constructor(props){
        super(props);
        this.handleClick = this.handleClick.bind(this)
        this.handleSubmit = this.handleSubmit.bind(this)
    }
    handleClick(terms){
        console.log("Hello")
    }
    handleSubmit(event){
        console.log("check check")
    }
    renderRequestBubble(terms){
        return(
            <RequestBubble
                requestItems={terms}
                onClick={() => this.handleClick(terms)}
            />
        )
    }
    render() {
        return(
            <div className='requestBox'>
                {this.renderRequestBubble(['Brazza','Le Petit Journal','1800-1900'])}
                <div className='graphingButtonContainer'>
                    <input
                        type='submit'
                        id='startGraphingButton'
                        value='Graph!'
                        onSubmit={this.handleSubmit}
                    />
                </div>
            </div>
        );

    }
}

function RequestBubble(props){
    return(
        <button className='requestBubble' onClick={props.onClick}>
            <ul>
                {props.requestItems.map(element =>
                    <li key={element}>{element}</li>)}
            </ul>
        </button>
    );
}


export default App;