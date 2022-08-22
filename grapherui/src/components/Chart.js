import HighchartsReact from "highcharts-react-official";
import Highcharts from "highcharts";
import React, {useContext} from "react";
import {GraphSettingsContext, GraphSettingsDispatchContext} from "./GraphSettingsContext";
import ToggleButton from '@mui/material/ToggleButton';
import ToggleButtonGroup from '@mui/material/ToggleButtonGroup';
import Button from '@mui/material/Button'
import Switch from "@mui/material/Switch";
import Slider from '@mui/material/Slider';
import useData from "./useData";
const syncColors = require("../utils/syncColors");
const generateOptions = require("../utils/generateOptions");
const getWidestDateSpan = require("../utils/getDateRangeSpan");

//TODO: write tests for component and utils
function Chart(props) {
    const allSettings = useContext(GraphSettingsContext)
    const chartSettings = allSettings[props.settingsID];
    const dateRange = getWidestDateSpan(props.tickets);
    const query =
        "/graphData?keys=" + Object.keys(props.tickets) +
        "&continuous=" + chartSettings.continuous +
        "&dateRange=" + dateRange +
        "&timeBin=" + chartSettings.timeBin +
        "&averageWindow=" + chartSettings.averageWindow;
    const series = useData(query);
    const graphDataWithSyncedColors = syncColors(
        series,
        allSettings);
    const highchartsOptions = generateOptions(
        graphDataWithSyncedColors,
        chartSettings);

    return (
        <div>
            <HighchartsReact
                highcharts={Highcharts}
                options={highchartsOptions}
            />
            <ChartSettings
                settingsID={props.settingsID}
            />
        </div>


    );
}
//TODO: labels
function ChartSettings(props){
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
                    timeBin: e.target.value
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
            <Slider
                aria-label="averageWindow"
                defaultValue={0}
                valueLabelDisplay="auto"
                step={1}
                marks={true}
                min={0}
                max={31}
                track={false}
                value={settingsForID.averageWindow}
                onChange={e => {
                    dispatch({
                        type: 'setAverageWindow',
                        key: props.settingsID,
                        averageWindow: e.target.value,
                    });
                }}
            />
            <Switch
                checked={settingsForID.continuous}
                onChange={e => {
                    dispatch({
                        type: 'setContinuous',
                        key: props.settingsID,
                        continuous: e.target.checked,
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