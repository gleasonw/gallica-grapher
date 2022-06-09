import React from "react";
import TicketLabel from "./TicketLabel";
import Chart from "./Chart";
import TicketPapers from "./TicketPapers";
import {useEffect, useState} from "react";

export function GroupedTicketResults(props) {
    const [averageWindow, setAverageWindow] = useState(0)
    const [groupOptions, setGroupOptions] = useState({});
    const [alignment, setAlignment] = React.useState('year');

    const handleChange = (event, newAlignment) => {
        if(event.target.name === 'timeBin'){
            if(newAlignment){
                setAlignment(newAlignment);
            }
        }else{
            setAverageWindow(event.target.value)
        }

    };

    useEffect(() => {
        const window = averageWindow ? averageWindow : 0;
        let updatedGroupOptions = {}
        let keys = Object.keys(props.tickets)
        fetch("/graphData?keys="+keys+"&averageWindow="+window+"&timeBin="+alignment)
            .then(res => res.json())
            .then(result => {
                updatedGroupOptions = result["options"]
                setGroupOptions(updatedGroupOptions)
            })
    }, [averageWindow, props.tickets, alignment]);

    return (
        <div className='groupedResultsUI'>
            <GroupedTicketLabelBar tickets={props.tickets}/>
            <GroupedChart
                onClick={props.handleClick}
                groupOptions={groupOptions}
                onChange={handleChange}
                timeBinVal={alignment}
                averageWindow={averageWindow}
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
    return (
        <div>
            <Chart
                options={props.groupOptions}
                onChange={props.onChange}
                timeBinVal={props.timeBinVal}
                averageWindow={props.averageWindow}
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