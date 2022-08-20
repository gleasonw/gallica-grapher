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

function Chart(props) {
    const settings = useContext(GraphSettingsContext)
    const settingsForID = settings[props.settingsID];
    const dateRange = getWidestDateRange(props.tickets);
    const query =
        "/graphData?keys=" + Object.keys(props.tickets) +
        "&continuous=" + settingsForID.continuous +
        "&dateRange=" + dateRange +
        "&timeBin=" + settingsForID.timeBin +
        "&averageWindow=" + settingsForID.averageWindow;
    const series = useData(query);
    const graphDataWithSyncedColors = syncColors(series, settings);
    const options = generateOptions(graphDataWithSyncedColors);

    //TODO: test this

    function syncColors(seriesToSync, settings){
        const keyColorPairs = Object.keys(props.tickets).map(key => {
            return {
                key: key,
                color: settings[key].color
            }
        });
        return seriesToSync.map(key => {
            const color = keyColorPairs.find(pair => pair.key === key.key).color;
            return {
                ...seriesToSync[key],
                color: color
            }
        });
    }

    function generateOptions(series){
        let options = {
            chart: {
                zoomType: 'x'
            },
            legend: {
                dateTimeLabelFormats: {
                    month: '%b',
                    year: '%Y'
                }
            },
            title: {
                text: null
            },
            yAxis: {
                title: {
                    text: 'Mentions'
                }
            },
            series: series
        }
        if(settings.timeBin === 'year'){
            function formatYearOptions(){
                options.plotOptions = {
                        line: {
                            marker: {
                                enabled: false
                            }
                        }
                    }
                options.xAxis = {
                        type: 'line'
                    }
            }
            formatYearOptions()
        }else if(settings.timeBin === 'month'){
            function formatYearMonOptions(){
                options.xAxis = {
                        type: 'datetime',
                        dateTimeLabelFormats: {
                            month: '%b',
                            year: '%Y'
                        }
                    }
            }
            formatYearMonOptions()
        }else{
            function formatYearMonDayOptions() {
                options.xAxis = {type: 'datetime'}
            }
            formatYearMonDayOptions()
        }
        return options;
    }

    function getWidestDateRange(tickets) {
        let widestDateRange = 0;
        let widestTicket = null;
        Object.keys(tickets).forEach(key => {
            const lowYear = tickets[key].dateRange[0];
            const highYear = tickets[key].dateRange[1];
            const thisWidth = highYear - lowYear;
            if (thisWidth > widestDateRange) {
                widestDateRange = thisWidth;
                widestTicket = key;
            }
        }
    )
    return tickets[widestTicket].dateRange;
}

    return (
        <div>
            <HighchartsReact
                highcharts={Highcharts}
                options={options}
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