import React, {useEffect, useReducer, useState} from 'react';
import GroupedTicketResults from "./GroupedTicketResults";
import Button from "@mui/material/Button"
import SoloTickets from "./SoloTickets";
import {GraphSettingsContext, GraphSettingsDispatchContext} from "./GraphSettingsContext";

function ResultUI(props){

    const [grouped, setGrouped] = useState(true);
    const [graphSettings, dispatch] = useReducer(
        settingsReducer,
        props.tickets,
        initGraphSettings);
    const [settingHistory, setSettingHistory] = useState({});

    useEffect(() => {
        const requestIDS = Object.keys(props.tickets);
        fetch(
            "/graphData?keys="+requestIDS+
            "&averageWindow=0&timeBin=year")
            .then(res => res.json())
            .then(result => {
                result["options"].map(key => (
                    dispatch({
                        type: 'setSeries',
                        key: key,
                        series: result
                    })
                ))
            })
    }, [props.tickets]);

    function handleClick(){
        grouped ?
            handleRestore() :
            stashIndividualOptionsHistory()
        setGrouped(!grouped)
    }

    function stashIndividualOptionsHistory(){
        setSettingHistory(graphSettings)
    }

    function handleRestore(){
        if(settingHistory){
            const newSettings = {
                ...settingHistory,
                group: graphSettings.group
            }
            dispatch({
                type: 'restoreSettings',
                settings: newSettings
            })
        }
    }

    function initGraphSettings(tickets){
        const initSetting = {
            timeBin: 'year',
            averageWindow: '0',
            continuous: 'false',
            series: []
        }
        let initialGraphSettings = {}
        tickets.map(key => (
            initialGraphSettings[key] = initSetting
        ));
        initialGraphSettings["group"] = initSetting
        return initialGraphSettings
    }

    return(
        <GraphSettingsContext value={graphSettings}>
            <GraphSettingsDispatchContext value={dispatch()}>
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
            </GraphSettingsDispatchContext>
        </GraphSettingsContext>
    )
}

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
            const newSeries = updateSeries(action);
            return {
                ...graphSettings,
                [action.key]: {
                    ...graphSettings[action.key],
                    timeBin: action.timeBin,
                    series: newSeries
                }
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
        }case 'restore': {
            return {}
        }
        default:
            throw Error("Unknown action: " + action.type);
    }
    function updateSeries(settings){
        let newSeries = {}
        fetch(
            "/graphData?keys=" + settings.key +
            "&averageWindow=" + settings.averageWindow +
            "&timeBin=" + settings.timeBin)
            .then(res => res.json())
            .then(result => {
                newSeries = result
            })
        return newSeries
    }
}
export default ResultUI;