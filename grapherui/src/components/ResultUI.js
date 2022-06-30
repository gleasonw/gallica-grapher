import React, {useEffect, useReducer, useState} from 'react';
import GroupedTicketResults from "./GroupedTicketResults";
import Button from "@mui/material/Button"
import SoloTickets from "./SoloTickets";
import {GraphSettingsContext, GraphSettingsDispatchContext} from "./GraphSettingsContext";

//TODO: break up individual settings and grouped settings in state
//TODO: use context for tickets.
function ResultUI(props){

    const [firstDegroup, setFirstDegroup] = useState(true);
    const [grouped, setGrouped] = useState(true);
    const [graphSettings, dispatch] = useReducer(
        settingsReducer,
        props.tickets,
        initGraphSettings)

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
            continuous: 'false'
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
                return {
                    ...graphSettings,
                    [action.key]: {
                        ...graphSettings[action.key],
                        timeBin: action.timeBin,
                    }
                }
            }else{
                return graphSettings
            }
        }case 'setAverageWindow': {
            return {
                ...graphSettings,
                [action.key]: {
                    ...graphSettings[action.key],
                    averageWindow: action.averageWindow,
                }
            }
        }case 'toggleContinuous': {
            return {
                ...graphSettings,
                [action.key]: {
                    ...graphSettings[action.key],
                    continuous: action.continuous,
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
}
export default ResultUI;