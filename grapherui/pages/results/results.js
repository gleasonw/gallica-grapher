import React, {useReducer, useState} from 'react';
import GroupedTicketResults from "./components/GroupedTicketResults";
import Button from "@mui/material/Button"
import SoloTickets from "./components/SoloTickets";
import settingsReducer from "./components/settingsReducer";
import {GraphSettingsContext, GraphSettingsDispatchContext} from "./components/GraphSettingsContext";

//TODO: use context for tickets.
function Results(props){

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

export default Results;