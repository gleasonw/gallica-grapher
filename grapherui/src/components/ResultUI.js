import React, {useReducer, useState} from 'react';
import GroupedTicketResults from "./GroupedTicketResults";
import FormGroup from '@mui/material/FormGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import Switch from "@mui/material/Switch";
import SoloTickets from "./SoloTickets";
import {GraphSettingsContext, GraphSettingsDispatchContext} from "./GraphSettingsContext";
import {settingsReducer} from "./SettingsReducer";
import {initGraphSettings} from "../utils/initGraphSettings";

function ResultUI(props){

    const [grouped, setGrouped] = useState(true);
    const [graphSettings, dispatch] = useReducer(
        settingsReducer,
        props.tickets,
        initGraphSettings)

    function handleGroupToggle(){
        setGrouped(!grouped)
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