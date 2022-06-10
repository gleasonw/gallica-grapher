import React, {useEffect, useState} from 'react';
import TicketLabel from "./TicketLabel";
import Chart from "./Chart";
import GroupedTicketResults from "./GroupedTicketResults";
import TicketPapers from "./TicketPapers";
import Button from "@mui/material/Button"

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
    const [graphSettings, setGraphSettings] = useState(starterSettings);
    const [graphSettingsHistory, setGraphSettingsHistory] = useState({});

    //Called on initial render
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
        if(grouped){
            restoreIndividualOptions();
            setGrouped(false);
        }else{
            stashIndividualOptionsHistory();
            setGrouped(true);
        }

    }
    function stashIndividualOptionsHistory(){
        setGraphSettingsHistory(graphSettings)

    }
    function restoreIndividualOptions(){
        setGraphSettings(graphSettingsHistory)
    }
    function handleChange(event, ticketID){
        const val = event.target.value;
        const name = event.target.name;
        let updatedSettings = structuredClone(graphSettings);
        updatedSettings[ticketID][name] = val;
        setGraphSettings(updatedSettings)
    }
    //Fetch new series when timeBin, averageWindow, or continuous changes
    function fetchNewSeries(key) {
        let updatedSettings = structuredClone(graphSettings);
        const settingsForKey = updatedSettings.key
        console.log(settingsForKey)
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
                <Button onClick={handleClick}>
                    Group
                </Button>
                <GroupedTicketResults
                    tickets={props.tickets}
                    settings={graphSettings["group"]}
                    onChange={handleChange}
                />
            </div>
        )
    }else{
        return(
            <div className='resultUI'>
                <Button onClick={handleClick}>
                    Group
                </Button>
                <div className='ticketResultsContainer'>
                    {Object.keys(props.tickets).map(key => (
                        <SoloTicketResult
                            terms={props.tickets[key]["terms"]}
                            papers={props.tickets[key]["papersAndCodes"]}
                            dateRange={props.tickets[key]["dateRange"]}
                            key={key}
                            requestID={key}
                            settings={graphSettings[key]}
                            onChange={handleChange}
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