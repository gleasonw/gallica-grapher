import HighchartsReact from "highcharts-react-official";
import Highcharts from "highcharts";
import React, {useContext} from "react";
import {GraphSettingsContext, GraphSettingsDispatchContext} from "./GraphSettingsContext";
import TextField from '@mui/material/TextField';
import ToggleButton from '@mui/material/ToggleButton';
import ToggleButtonGroup from '@mui/material/ToggleButtonGroup';
import Button from '@mui/material/Button'
import Switch from "@mui/material/Switch";

function Chart(props) {
    return (
        <div>
            <HighchartsReact
                highcharts={Highcharts}
                options={props.options}
            />
            <ChartOptions
                settingsID={props.settingsID}
            />
        </div>


    );
}

function ChartOptions(props){
    const settings = useContext(GraphSettingsContext);
    const settingsForID = settings[props.settingsID];
    const dispatch = useContext(GraphSettingsDispatchContext)
    return(
        <div>
            <ToggleButtonGroup
              value={settingsForID.timeBin}
              exclusive
              onChange={e => {
                dispatch({
                    type: 'setTimeBin',
                    key: props.settingsID,
                    timeBin: e.target.valueOf()
                })
              }}
              aria-label="Time bin size selection"
            >

                <ToggleButton
                    value="year"
                    aria-label="year-grouped"
                    name='timeBin'
                >
                    year
                </ToggleButton>

                <ToggleButton
                    value="month"
                    aria-label="month-grouped"
                    name='timeBin'
                >
                    month
                </ToggleButton>

                <ToggleButton
                    value="day"
                    aria-label="day-grouped"
                    name='timeBin'
                >
                    day
                </ToggleButton>

            </ToggleButtonGroup>

            <TextField
                value={props.averageWindow}
                onChange={e => {
                    dispatch({
                        type: 'setTimeBin',
                        key: props.settingsID,
                        averageWindow: e.target.value,
                    });
                }}
                name='averageWindow'
                label='Rolling average'
                type='number'
            />

            <Switch
                checked={props.continuous}
                onChange={e => {
                    dispatch({
                        type: 'setContinuous',
                        key: props.settingsID,
                        continuous: e.target.valueOf(),
                    })
                }}
                label='require continuous newspapers'
            />

            <Button variant="text">
                Download PNG
            </Button>

        </div>

    )
}

export default Chart;