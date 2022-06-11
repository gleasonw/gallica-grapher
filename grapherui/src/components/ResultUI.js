// noinspection JSCheckFunctionSignatures

import React, {useEffect, useReducer, useState} from 'react';
import GroupedTicketResults from "./GroupedTicketResults";
import Button from "@mui/material/Button"
import SoloTickets from "./SoloTickets";

function ResultUI(props){

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
                    handleSetSeries({
                        key: key,
                        series: result
                    })
                ))
            })
    }, [props.tickets]);

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
                return {
                    ...graphSettings,
                    [action.key]: {
                        ...graphSettings[action.key],
                        timeBin: action.timeBin,
                        series: action.series
                    }
                }
            }case 'setAverageWindow': {
                return {
                    ...graphSettings,
                    [action.key]: {
                        ...graphSettings[action.key],
                        averageWindow: action.averageWindow,
                        series: action.series
                    }
                }
            }case 'toggleContinuous': {
                return {
                    ...graphSettings,
                    [action.key]: {
                        ...graphSettings[action.key],
                        continuous: !graphSettings[action.key].continuous,
                        series: action.series
                    }
                }
            }case 'restore': {
                return {}
            }
            default:
                throw Error("Unknown action: " + action.type);
        }

    }

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

    function handleUpdateTimeBin(ticket){
        const newSeries = updateSeries(ticket);
        dispatch({
            type: 'setTimeBin',
            key: ticket.key,
            timeBin: ticket.timeBin,
            series: newSeries
        })
    }

    function handleUpdateAverageWindow(ticket){
        const newSeries = updateSeries(ticket);
        dispatch({
            type: 'setTimeBin',
            key: ticket.key,
            averageWindow: ticket.averageWindow,
            series: newSeries
        })
    }

    function handleUpdateContinuous(ticket){
        const newSeries = updateSeries(ticket);
        dispatch({
            type: 'setTimeBin',
            key: ticket.key,
            continuous: ticket.continuous,
            series: newSeries
        })
    }

    function handleSetSeries(ticket){
        dispatch({
            type: 'setSeries',
            key: ticket.key,
            series: ticket.series
        })
    }

    function updateSeries(settings){
        const keys = settings.key === "group" ?
            Object.keys(props.tickets) :
            [settings.key]
        let newSeries = {}
        fetch(
            "/graphData?keys=" + keys +
            "&averageWindow=" + settings.averageWindow +
            "&timeBin=" + settings.timeBin)
            .then(res => res.json())
            .then(result => {
                newSeries = result
            })
        return newSeries
    }

    return(
        <div className='resultUI'>
            <Button onClick={handleClick}>
                Group
            </Button>
            {grouped ? (
                <GroupedTicketResults
                    tickets={props.tickets}
                    groupSettings={graphSettings.group}
                    onSetTimeBin={handleUpdateTimeBin}
                    onSetAverageWindow={handleUpdateAverageWindow}
                    onSetContinuous={handleUpdateContinuous}
                />
            ) : (
                <SoloTickets
                    tickets={props.tickets}
                    onSetTimeBin={handleUpdateTimeBin}
                    onSetAverageWindow={handleUpdateAverageWindow}
                    onSetContinuous={handleUpdateContinuous}
                    settings={graphSettings}
                />
            )}
        </div>
    )
}

export default ResultUI;