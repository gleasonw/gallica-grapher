import React, {useEffect, useState} from 'react';
import ReactSlider from 'react-slider';
import Highcharts from 'highcharts'
import HighchartsReact from 'highcharts-react-official'

function UserInputForm(props){
    return(
        <form onSubmit={props.onSubmit} className='userInputForm'>
            <TermInputBox
                value={props.termInputValue}
                onChange={props.onChange}
                onKeyDown={props.onKeyDown}
                selectedTerms={props.selectedTerms}
                deleteTermBubble={props.deleteTermBubble}
            />
            <br />
            <PaperInputBox
                onClick={props.onPaperDropItemClick}
                onChange={props.onChange}
                onKeyDown={props.onKeyDown}
                selectedPapers={props.selectedPapers}
                deletePaperBubble={props.deletePaperBubble}
                value={props.paperInputValue}
            />
            <br />
            <DateInputBox
                onChange={props.onChange}
                minYear={props.minYear}
                maxYear={props.maxYear}
                lowYear={props.lowYearValue}
                highYear={props.highYearValue}
            />
            <input
                type='button'
                id='createTicketButton'
                value='Create Ticket'
                onClick={props.onClick}
            />
        </form>
    )
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
        this.props.selectedPapers.map(paperAndCode => paperNames.push(paperAndCode['paper']))
        return(
            <div>
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

function DateInputBox(props){
    const [error, setError] = useState(null);
    const [isLoaded, setIsLoaded] = useState(false);
    const [items, setItems] = useState([]);
    useEffect(() => {
            fetch("/paperchartjson")
                .then(res => res.json())
                .then(
                    (result) => {
                        setIsLoaded(true);
                        setItems(result);
                    },
                    (error) => {
                        setIsLoaded(true);
                        setError(error);
                    }
                )
        console.log("nice")
    }, []);
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
            series: [items],
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
                    value={[props.lowYear, props.highYear]}
                    max={props.maxYear}
                    min={props.minYear}
                    pearling
                    onChange={props.onChange}
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

export default UserInputForm;