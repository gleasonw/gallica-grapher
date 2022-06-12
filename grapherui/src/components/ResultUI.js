import React, {useEffect, useReducer, useState} from 'react';
import GroupedTicketResults from "./GroupedTicketResults";
import Button from "@mui/material/Button"
import SoloTickets from "./SoloTickets";
import {GraphSettingsContext, GraphSettingsDispatchContext} from "./GraphSettingsContext";


//TODO: use context for tickets.
function ResultUI(props){

    const [firstDegroup, setFirstDegroup] = useState(true);
    const [grouped, setGrouped] = useState(true);
    const [graphSettings, dispatch] = useReducer(
        settingsReducer,
        props.tickets,
        initGraphSettings)

    //TODO: Catch errors on fetch
    useEffect(() => {
        const requestIDS = Object.keys(props.tickets);
        fetch(
            "/graphData?keys="+requestIDS+
            "&averageWindow=0&timeBin=year")
            .then(res => res.json())
            .then(result => {
                dispatch({
                    type: 'setSeries',
                    key: 'group',
                    series: result.series
                })
            })
    }, [props.tickets]);

    function handleClick(){
        if(firstDegroup && grouped){
            populateTicketSettingsFromGroup()
            setFirstDegroup(false)
        }
        setGrouped(!grouped)
    }

    function populateTicketSettingsFromGroup(){
        const groupSettings = graphSettings.group;
        const groupSeries = groupSettings.series;
        groupSeries.map(key => (
            dispatch({
                type: 'setTicketSettings',
                key: key,
                settings: {
                    ...groupSettings,
                    series: groupSeries[key]
                }
            })
        ))
    }

    function initGraphSettings(tickets){
        const initSetting = {
            timeBin: 'year',
            averageWindow: '0',
            continuous: 'false',
            series: []
        }
        let initialGraphSettings = {}
        Object.keys(tickets).map(key => (
            initialGraphSettings[key] = initSetting
        ));
        initialGraphSettings["group"] = initSetting
        return initialGraphSettings
    }

    return(
        <GraphSettingsContext.Provider value={graphSettings}>
            <GraphSettingsDispatchContext.Provider value={dispatch}>
                <div className='resultUI'>
                    <Button onClick={handleClick}>
                        Group
                    </Button>
                    {grouped ? (
                        <GroupedTicketResults
                            tickets={props.tickets}
                        />
                    ) : (
                        <SoloTickets
                            tickets={props.tickets}
                        />
                    )}
                </div>
            </GraphSettingsDispatchContext.Provider>
        </GraphSettingsContext.Provider>
    )
}
//TODO: Async updates.
function settingsReducer(graphSettings, action){
    switch (action.type){
        case 'setSeries' : {
            return {
                ...graphSettings,
                [action.key]: {
                    ...graphSettings[action.key],
                    series: action.series
                }
            }
        }
        case 'setTimeBin': {
            if(action.timeBin){
                const newSeries = updateSeries(action);
                return {
                    ...graphSettings,
                    [action.key]: {
                        ...graphSettings[action.key],
                        timeBin: action.timeBin,
                        series: newSeries
                    }
                }
            }else{
                return graphSettings
            }
        }case 'setAverageWindow': {
            const newSeries = updateSeries(action);
            return {
                ...graphSettings,
                [action.key]: {
                    ...graphSettings[action.key],
                    averageWindow: action.averageWindow,
                    series: newSeries
                }
            }
        }case 'toggleContinuous': {
            const newSeries = updateSeries(action);
            return {
                ...graphSettings,
                [action.key]: {
                    ...graphSettings[action.key],
                    continuous: action.continuous,
                    series: newSeries
                }
            }
        }case 'setTicketSettings': {
            return {
                ...graphSettings,
                [action.key]: action.settings
            }
        }
        default:
            throw Error("Unknown action: " + action.type);
    }
    function updateSeries(settings){
        //TODO: A wonky way of getting the keys. I feel I could organize better.
        const averageWindow = settings.averageWindow ?
            settings.averageWindow : 0;
        const ticketIDs = settings.key === 'group' ?
            Object.keys(graphSettings).filter(key => key !== 'group') :
            settings.key
        return fetch(
            "/graphData?keys=" + ticketIDs +
            "&averageWindow=" + averageWindow +
            "&timeBin=" + settings.timeBin)
            .then(res => res.json())
            .then(
                (result) => {
                    return result
                },
                (error) => {
                    return error
                }
            )
    }
}
export default ResultUI;