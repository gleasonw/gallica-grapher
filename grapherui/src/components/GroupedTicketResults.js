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
        <div>
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
            />
        </div>

    )
}

function GroupedTicketLabelBar(props) {
    return (
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
            <GroupedTicketStat/>
            <GroupedTicketStat/>
            <GroupedTicketStat/>
            <GroupedTicketStat/>
            <GroupedTicketStat/>
        </div>
    );
}

function GroupedTicketStat(props) {
    return (
        <div className='groupedStat'>
            <TicketLabel
                terms={['nice']}
                papers={[{'code': '35135', 'paper': 'nice'}]}
                dateRange={[1789, 1902]}
            />
            <TicketPapers
                onClick={props.onClick}
            />
        </div>
    )
}

export default GroupedTicketResults;