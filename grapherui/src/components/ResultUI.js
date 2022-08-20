import React, {useReducer, useState} from 'react';
import GroupedTicketResults from "./GroupedTicketResults";
import FormGroup from '@mui/material/FormGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import Switch from "@mui/material/Switch";
import SoloTickets from "./SoloTickets";
import {GraphSettingsContext, GraphSettingsDispatchContext} from "./GraphSettingsContext";
import {settingsReducer} from "./SettingsReducer";

//TODO: break up individual settings and grouped settings in state
//TODO: use context for tickets.
function ResultUI(props){

    const [grouped, setGrouped] = useState(true);
    const [graphSettings, dispatch] = useReducer(
        settingsReducer,
        props.tickets,
        initGraphSettings)

    function handleGroupToggle(){
        setGrouped(!grouped)
    }

    function initGraphSettings(tickets){
        const highChartsSeriesColors = [
            '#7cb5ec',
            '#434348',
            '#90ed7d',
            '#f7a35c',
            '#8085e9',
            '#f15c80',
            '#e4d354',
            '#2b908f',
            '#f45b5b',
            '#91e8e1'];
        let indexForColorAssignment = 0;
        const initSetting = {
            timeBin: 'year',
            averageWindow: '0',
            continuous: 'false'
        }
        let initialGraphSettings = {}
        for (let key in tickets){
            initialGraphSettings[key] = {
                ...initSetting,
                color: highChartsSeriesColors[indexForColorAssignment]
            }
            indexForColorAssignment =
                (indexForColorAssignment + 1) %
                highChartsSeriesColors.length;
        }
        initialGraphSettings["group"] = initSetting;
        return initialGraphSettings
    }

    return(
        <GraphSettingsContext.Provider value={graphSettings}>
            <GraphSettingsDispatchContext.Provider value={dispatch}>
                <div className='resultUI'>
                    {Object.keys(props.tickets).length > 1  &&
                        <FormGroup>
                            <FormControlLabel
                                labelPlacement="bottom"
                                control={
                                    <Switch
                                        checked={grouped}
                                        onChange={handleGroupToggle}
                                    />
                                }
                                label={grouped ? 'Ungroup' : 'Group'}
                            />
                        </FormGroup>
                    }
                    {grouped ? (
                        <GroupedTicketResults
                            tickets={props.tickets}
                        />
                    ) : (
                        <SoloTickets
                            tickets={props.tickets}
                        />
                    )}
                    }
                </div>
            </GraphSettingsDispatchContext.Provider>
        </GraphSettingsContext.Provider>
    )
}
export default ResultUI;