import React, {useEffect, useState} from "react";
import TicketLabel from "./TicketLabel";
import Chart from "./Chart";
import TicketPapers from "./TicketPapers";

export function GroupedTicketResults(props) {
    return (
        <div className='groupedResultsUI'>
            <GroupedTicketLabelBar tickets={props.tickets}/>
            <GroupedChart
                settings={props.groupSettings}
                ticketSettings={props.ticketSettings}
                onChange={props.onChange}
            />
            <GroupedStatBar
                onClick={props.handleClick}
                paperStats={props.paperStats}
                tickets={props.tickets}
            />
        </div>

    )
}
//TODO: Sync label color with line color
function GroupedTicketLabelBar(props) {
    return (
        <div className='groupedLabelBar'>
            {Object.keys(props.tickets).map(key => (
                <div className = 'groupedLabel'>
                    <TicketLabel
                        terms={props.tickets[key]['terms']}
                        papers={props.tickets[key]['papersAndCodes']}
                        dateRange={props.tickets[key]['dateRange']}
                        key={key}
                    />
                </div>
            ))}
        </div>
    );
}

function GroupedChart(props) {
    const timeBin = props.groupSettings["timeBin"];
    const keyedSeries = structuredClone(props.ticketSettings["series"]);
    const [options, setOptions] = useState({});
    useEffect(() => {
        let groupedSeries = []
        groupSeries()
        let options = {
            chart: {
                zoomType: 'x'
            },
            legend: {
                dateTimeLabelFormats: {
                    month: '%b',
                    year: '%Y'
                }
            },
            title: {
                text: null
            },
            yAxis: {
                title: {
                    text: 'Mentions'
                }
            },
            series: groupedSeries
        }
        if(timeBin === 'year'){
            function formatYearOptions(){
                options.plotOptions = {
                        line: {
                            marker: {
                                enabled: false
                            }
                        }
                    }
                options.xAxis = {
                        type: 'line'
                    }
            }
            formatYearOptions()
        }else if(timeBin === 'month'){
            function formatYearMonOptions(){
                options.xAxis = {
                        type: 'datetime',
                        dateTimeLabelFormats: {
                            month: '%b',
                            year: '%Y'
                        }
                    }
            }
            formatYearMonOptions()
        }else{
            function formatYearMonDayOptions() {
                options.xAxis = {type: 'datetime'}
            }
            formatYearMonDayOptions()
        }
        function groupSeries(){
            groupedSeries.push(
                Object.keys(keyedSeries).map(key =>
                keyedSeries[key]
            ))
        }
        setOptions(options)
    },[keyedSeries, timeBin])

    return (
        <div>
            <Chart
                options={options}
                onChange={() => props.onChange}
                continuous={props.groupSettings["continuous"]}
                timeBinVal={props.groupSettings["timeBin"]}
                averageWindow={props.groupSettings["averageWindow"]}
            />
        </div>
    )
}

function GroupedStatBar(props) {
    return (
        <div className='groupedStatBar'>
            {Object.keys(props.tickets).map(key => (
                <GroupedTicketStat
                    terms={props.tickets[key]['terms']}
                    papers={props.tickets[key]['papersAndCodes']}
                    dateRange={props.tickets[key]['dateRange']}
                    ticketID={key}
                    key={key}
                />
            ))}
        </div>
    );
}

function GroupedTicketStat(props) {
    return (
        <div className='groupedStat'>
            <TicketLabel
                terms={props.terms}
                papers={props.papers}
                dateRange={props.dateRange}
            />
            <TicketPapers
                ticketID={props.ticketID}
                continuous={false}
                dateRange={props.dateRange}
            />
        </div>
    )
}

export default GroupedTicketResults;