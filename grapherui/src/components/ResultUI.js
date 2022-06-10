import React, {useEffect, useState, useCallback} from 'react';
import TicketLabel from "./TicketLabel";
import Chart from "./Chart";
import GroupedTicketResults from "./GroupedTicketResults";
import TicketPapers from "./TicketPapers";

function ResultUI(props){
    let starterSettings = {}
    props.tickets.map(key => (
        starterSettings[key] = {
            timeBin: 'year',
            averageWindow: '0',
            continuous: 'false',
            series: {}
        }
    ));
    starterSettings["group"] = {
        timeBin: 'year',
        averageWindow: '0',
        continuous: 'false',
        series: {}
    }
    const [grouped, setGrouped] = useState(true);
    const [graphSettings, setGraphSettings] = useState({starterSettings: starterSettings});
    const [graphSettingsHistory, setGraphSettingsHistory] = useState({});

    //Called once on initial render
    useEffect(() => {
        const requestIDS = Object.keys(props.tickets);
        let starterSettings = {};
        fetch(
            "/graphData?keys=" + requestIDS + "&averageWindow=0&timeBin=year")
            .then(res => res.json())
            .then(result => {
                result["options"].map(key => (
                    starterSettings[key] = key.options
                ))
            })
    }, [props.tickets]);

    //Toggle grouped
    function handleClick(){

    }
    //Store individual prop settings on group
    function stashIndividualOptionsHistory(){

    }
    //Restore individual prop settings on degroup
    function restoreIndividualOptions(){

    }
    // Set new timeBin, averageWindow, or continuous, for given key, then call fetchNewSeries to update key's series
    function onChange(){

    }
    //Fetch new series when timeBin, averageWindow, or continuous changes
    function fetchNewSeries(key) {
        let updatedSettings = structuredClone(graphSettings);
        const settingsForKey = updatedSettings.key
        fetch(
            "/graphData?keys=" + key +
            "&averageWindow=" + settingsForKey.averageWindow +
            "&timeBin=" + settingsForKey.timeBin)
            .then(res => res.json())
            .then(result => {
                //set key's series to result
            })
    }



    if(grouped){
        return(
            <div className='resultUI'>
                <button className='graphGroupButton'>
                    Group
                </button>
                <GroupedTicketResults
                    tickets={props.tickets}
                    settings={graphSettings.group}
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
                            terms={props.tickets.key.terms}
                            papers={props.tickets.key.papersAndCodes}
                            dateRange={props.tickets.key.dateRange}
                            key={key}
                            requestID={key}
                            settings={graphSettings.key}
                            setIndividualOptions={() => handleIndividualOptionsChange}
                        />
                    ))}
                </div>
            </div>
        )
    }

}
//TODO: Pass graph settings up, send them to group ticket result, only fetch when necessary
function SoloTicketResult(props) {

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