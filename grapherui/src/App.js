import React from 'react';
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
            <MainContainer/>
        </div>
    );
}

class MainContainer extends React.Component {
    render(){
        return(
            <div className="mainContainer">
                <FormBox/>
                <RequestBox/>
            </div>
        )
    }
}

class FormBox extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            terms: [],
            papers: [],
            dateRange: null
        };
        this.handleInputChange = this.handleInputChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    handleInputChange(event) {
        const target = event.target;
        const value = target.type === 'checkbox' ? target.checked : target.value;
        const name = target.name;
        this.setState({
            [name]: value
        });
    }
    handleSubmit(event) {
        event.preventDefault()
    }
    render() {
        return (
            <form onSubmit ={this.handleSubmit} className='formBox'>
                <TermInputBox
                    handleInputChange={() => this.handleInputChange()}
                />
                <br />
                <PaperInputBox
                    handleInputChange={() => this.handleInputChange()}
                />
                <br />
                <DateInputBox
                    handleInputChange={() => this.handleInputChange()}
                />
                <input
                    type='submit'
                    id='createTicketButton'
                    value='Create Ticket'
                />
            </form>
        )
    }

}

class TermInputBox extends React.Component{
    render() {
        return(
            <div className='inputContainer'>
                <SelectionBox/>
                <input
                    type="text"
                    name="terms"
                    placeholder="Enter a term..."
                    onChange={this.props.handleInputChange}/>
            </div>
        )
    }
}

class PaperInputBox extends React.Component{
    render() {
        return(
            <div className='inputContainer'>
                <SelectionBox/>
                <input
                    type="text"
                    name="papers"
                    placeholder="Search for a paper to restrict search..."
                    onChange={this.props.handleInputChange}
                />
            </div>
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
            console.log(paperJSON)
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
                        thumbClassName="example-thumb"
                        trackClassName="example-track"
                        defaultValue={[0, 100]}
                        ariaLabel={['Lower thumb', 'Upper thumb']}
                        ariaValuetext={state => `Thumb value ${state.valueNow}`}
                        renderThumb={(props, state) => <div {...props}>{state.valueNow}</div>}
                        pearling
                        minDistance={10}
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

class SelectionBubble extends React.Component {
    render(){
        const selection = this.props.selection
        return (
        <div className='selectionBubble' id={selection}>
            <div className='delete'>X</div>
            <div className="selection">{selection}</div>
        </div>
        );
    }
}

class SelectionBox extends React.Component {
    render(){
        return(
            <div className='bubblesContainer'>
            </div>
        )
    }
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
                {props.requestItems.map(element => <li>{element}</li>)}
            </ul>
        </button>
    );
}


export default App;