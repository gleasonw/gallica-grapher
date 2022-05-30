import React, {useState, useEffect} from 'react';
import TicketLabel from "./TicketLabel";
import Highcharts from 'highcharts'
import HighchartsReact from 'highcharts-react-official'

function ResultUI(props){
    const [JSONGraphData, setJSONGraphData] = useState([]);
    const [paperAndOtherStats, setPaperAndOtherStats] = useState([]);
    const [grouped, setGrouped] = useState(true);
    useEffect(() => {
        //Fetch graph data, stats, assign requestID to each
        }
    )

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
                    tickets={props.tickets}
                />
                <Graph
                    onClick={handleClick}
                    graphingData={JSONGraphData}
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
            <div className='ticketLabel'>
                <TicketLabel
                terms={['nice']}
                papers={[{'code':'35135','paper':'nice'}]}
                dateRange={[1789,1902]}
                />
            </div>
            <div className='ticketLabel'>
                <TicketLabel
                terms={['nice']}
                papers={[{'code':'35135','paper':'nice'}]}
                dateRange={[1789,1902]}
                />
            </div>
            <div className='ticketLabel'>
                <TicketLabel
                terms={['nice']}
                papers={[{'code':'35135','paper':'nice'}]}
                dateRange={[1789,1902]}
                />
            </div>

            {/*{props.tickets.map(ticket => (*/}
            {/*    <TicketLabel*/}
            {/*        terms={ticket['terms']}*/}
            {/*        papers={ticket['papersAndCodes']}*/}
            {/*        dateRange={ticket['dateRange']}*/}
            {/*    />*/}
            {/*))}*/}
        </div>
    );
}

function Graph(props) {
    const options = {
        title: {
            text: 'Solar Employment Growth by Sector, 2010-2016'
            },
        subtitle: {
            text: 'Source: thesolarfoundation.com'
            },
        yAxis: {
            title: {
                text: 'Number of Employees'
            }
        },
        xAxis: {
            accessibility: {
                rangeDescription: 'Range: 2010 to 2017'
            }
        },
        legend: {
            layout: 'vertical',
                align: 'right',
                verticalAlign: 'middle'
        },
        plotOptions: {
            series: {
                label: {
                    connectorAllowed: false
                }
            ,
                pointStart: 2010
            }
        },
        series: [{
            name: 'Installation',
            data: [43934, 52503, 57177, 69658, 97031, 119931, 137133, 154175]
        }, {
            name: 'Manufacturing',
            data: [24916, 24064, 29742, 29851, 32490, 30282, 38121, 40434]
        }, {
            name: 'Sales & Distribution',
            data: [11744, 17722, 16005, 19771, 20185, 24377, 32147, 39387]
        }, {
            name: 'Project Development',
            data: [null, null, 7988, 12169, 15112, 22452, 34400, 34227]
        }, {
            name: 'Other',
            data: [12908, 5948, 8105, 11248, 8989, 11816, 18274, 18111]
        }],
        responsive: {
            rules: [{
                condition: {
                    maxWidth: 500
                },
                chartOptions: {
                    legend: {
                        layout: 'horizontal',
                        align: 'center',
                        verticalAlign: 'bottom'
                    }
                }
            }]
        }
    }
    return(
        <div>
            <DownloadButton
                text='Download Graph'
                onClick={() => props.onClick}
            />
            <HighchartsReact
                highcharts={Highcharts}
                options={options}
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