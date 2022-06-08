import React, {useEffect, useState} from 'react';
import TicketLabel from "./TicketLabel";
import Chart from "./Chart";
import GroupedTicketResults from "./GroupedTicketResults";
import TicketPapers from "./TicketPapers";

function ResultUI(props){
    const [paperStats, setPaperStats] = useState([]);
    const [grouped, setGrouped] = useState(true);
    //Testing
    const [tickets, setTickets] = useState({})

    function handleClick() {
        console.log("Here you go")
    }
    if(grouped){
        return(
            <div className='resultUI'>
                <button className='graphGroupButton'>
                    Group
                </button>
                <GroupedTicketResults
                    tickets={tickets}
                    onClick={handleClick}
                    paperStats={paperStats}
                />
            </div>
        )
    }else{
        return(
            <div className='resultUI'>
                <input type='button' className='graphGroupButton'/>
                <div className='ticketResultsContainer'>
                    {Object.keys(props.tickets).map(key => (
                        <SoloTicketResult
                            terms={props.tickets[key]["terms"]}
                            papers={props.tickets[key]['papersAndCodes']}
                            dateRange={props.tickets[key]['terms']}
                            key={key}
                        />
                    ))}
                </div>
            </div>
        )
    }

}
//TODO: Pass graph settings up, send them to group ticket result, only fetch when necessary
function SoloTicketResult(props) {
    const [timeBin, setTimeBin] = useState('year');
    const [averageWindow, setAverageWindow] = useState(0)
    const [groupOptions, setGroupOptions] = useState({});

    useEffect(() => {
        let updatedGroupOptions = {}
        fetch("/graphData?keys="+props.key+"&averageWindow="+averageWindow+"&timeBin="+timeBin)
            .then(res => res.json())
            .then(result => {
                updatedGroupOptions = result["options"]
                setGroupOptions(updatedGroupOptions)
            })
    }, []);

    return (
        <div className='ticketResults'>
            <TicketLabel
                terms={props.terms}
                papers={props.papers}
                dateRange={props.dateRange}
            />
            <Chart options={props.options}/>
            <TicketPapers onClick={props.onClick}/>
        </div>
    )
}

export default ResultUI;