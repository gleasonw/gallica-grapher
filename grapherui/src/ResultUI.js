import React, {useState, useEffect} from 'react';
import TicketLabel from "./TicketLabel";
import Highcharts from 'highcharts'
import HighchartsReact from 'highcharts-react-official'

function ResultUI(props){
    const [JSONGraphData, setJSONGraphData] = useState([]);
    const [paperAndOtherStats, setPaperAndOtherStats] = useState([]);
    const [grouped, setGrouped] = useState(true);
    const [timeBin, setTimeBin] = useState('month');
    const [averageWindow, setAverageWindow] = useState(0)
    const [dateCategories, setDateCategories] = useState([])
    //Testing
    const [tickets, setTickets] = useState({'1234':
                                                        {
                                                            "terms": ["malamine"],
                                                            "papersAndCodes": [],
                                                            "dateRange": [1800, 1900],
                                                        }
                                                    })

    useEffect(() => {
        let updatedGraphData = []
        for(const key in tickets){
            fetch("/graphData?key="+key+"&averageWindow="+averageWindow+"&timeBin="+timeBin)
                .then(res => res.json())
                .then(result => {
                    let graphJSON = JSON.parse(result["graphJSON"])
                    updatedGraphData.push(graphJSON)
                })
        }
        setJSONGraphData(updatedGraphData)
    }, [averageWindow, tickets, timeBin]);

    function handleClick() {
        console.log("Here you go")
    }
    if(grouped){
        return(
            <div className='resultUI'>
                <button className='graphGroupButton'>
                    Group
                </button>
                <GroupedTicketLabelBar
                    tickets={tickets}
                />
                <Graph
                    onClick={handleClick}
                    graphingData={JSONGraphData}
                    timeBin={timeBin}
                    tickets={tickets}
                />
                <GroupedTicketInfoBar
                    onClick={handleClick}
                    paperAndOtherStats={paperAndOtherStats}
                />
            </div>
        )
    }else{
        return(
            <div className='resultUI'>
                <input type='button' className='graphGroupButton'/>
                <div className='ticketResultsContainer'>
                    <TicketResult
                        onClick={handleClick}
                    />
                    <TicketResult
                        onClick={handleClick}
                    />
                    <TicketResult
                        onClick={handleClick}
                    />
                </div>
            </div>
        )
    }

}
function GroupedTicketLabelBar(props) {
    return(
        <div className='groupedLabelBar'>
            {Object.keys(props.tickets).map(key => (
                <TicketLabel
                    terms={props.tickets[key]['terms']}
                    papers={props.tickets[key]['papersAndCodes']}
                    dateRange={props.tickets[key]['terms']}
                    key={key}
                />
            ))}
        </div>
    );
}

function Graph(props) {
    const [dateCategories, setDateCategories] = useState([]);
    useEffect(() => {
        function generatePartialDateCategories() {
            const lowDates = Object.keys(props.tickets).map(key => (
                props.tickets[key]["dateRange"][0]
            ))
            const highDates = Object.keys(props.tickets).map(key => (
                props.tickets[key]["dateRange"][1]
            ))
            const lowestDate = Math.min(...lowDates)
            const highestDate = Math.max(...highDates)
            let categories = []
            if (props.timeBin === 'month') {
                categories = generateMonthCategories(lowestDate, highestDate)
            } else {
                categories = generateYearCategories(lowestDate, highestDate)
            }
            setDateCategories(categories)
        }

        function generateMonthCategories(lowYear, highYear) {
            let range = genRange(lowYear, highYear)
            return range.map(year => (
                [...Array(12).keys()].map(month => (
                        (year + lowYear).toString() + "/" + (month + 1).toString()
                    )
                )
            )).flat()
        }

        function generateYearCategories(lowYear, highYear) {
            let range = genRange(lowYear, highYear)
            return range.map(year => (
                (year + lowYear).toString()
            )).flat()
        }

        function genRange(lowYear, highYear) {
            const delta = ((highYear - lowYear) + 1)
            return [...Array(delta).keys()]
        }
        if(props.timeBin === "year" || props.timeBin === "month"){
            generatePartialDateCategories()
        }
    }, [props.tickets, props.timeBin])
    return(
        <div>
            <DownloadButton
                text='Download Graph'
                onClick={() => props.onClick}
            />
            <HighchartsReact
                highcharts={Highcharts}
                options={props.options}
            />
        </div>
    );
}
function GroupedTicketInfoBar(props) {
    return(
        <div className='groupedInfoBar'>
            <div className='groupedStat'>
                <TicketLabel
                    terms={['nice']}
                    papers={[{'code':'35135','paper':'nice'}]}
                    dateRange={[1789,1902]}
                />
                <TicketStats
                    onClick={props.onClick}
                />
            </div>
            <div className='groupedStat'>
                <TicketLabel
                    terms={['nice']}
                    papers={[{'code':'35135','paper':'nice'}]}
                    dateRange={[1789,1902]}
                />
                <TicketStats
                    onClick={props.onClick}
                />
            </div>
            <div className='groupedStat'>
                <TicketLabel
                    terms={['nice']}
                    papers={[{'code':'35135','paper':'nice'}]}
                    dateRange={[1789,1902]}
                />
                <TicketStats
                    onClick={props.onClick}
                />
            </div>
        </div>
    );
}
function DownloadButton(props) {
    return(
        <button className='downloadButton' onClick={props.onClick}>
            {props.text}
        </button>
    );
}

function TicketStats(props) {
    return(
        <div className='ticketStats'>
            <ul>
                <li>Le Petit journal</li>
                <li>Le Figaro</li>
            </ul>
            <DownloadButton
                text={'Download CSV'}
                onClick={props.onClick}
            />
        </div>
    )
}

function TicketResult(props) {
    return (
        <div className='ticketResults'>
            <TicketLabel
                terms={['nice']}
                papers={[{'code':'35135','paper':'nice'}]}
                dateRange={[1789,1902]}
            />
            <Graph/>
            <TicketStats
                onClick={props.onClick}
            />
        </div>
    )
}

export default ResultUI;