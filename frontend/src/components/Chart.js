import HighchartsReact from "highcharts-react-official";
import Highcharts from "highcharts";
import React, {useContext, useRef} from "react";
import {GraphSettingsContext, GraphSettingsDispatchContext} from "./GraphSettingsContext";
import ToggleButton from '@mui/material/ToggleButton';
import InputLabel from '@mui/material/InputLabel';
import FormControl from '@mui/material/FormControl';
import useData from "./hooks/useData";
import {MenuItem, Select} from "@mui/material";
import syncColors from  "../utils/syncColors";
import generateOptions from "../utils/generateOptions";
import getDateRangeSpan from "../utils/getDateRangeSpan";
import {CSVDownload} from "react-csv";

require("highcharts/modules/exporting")(Highcharts);
require("highcharts/modules/export-data")(Highcharts);

function Chart(props) {
    const allSettings = useContext(GraphSettingsContext)
    const chartSettings = allSettings[props.settingsID];
    const dateRange = getDateRangeSpan(props.tickets);
    const chartRef = useRef(null);
    const query =
        "/api/graphData?keys=" + Object.keys(props.tickets) +
        "&continuous=" + chartSettings.continuous +
        "&dateRange=" + dateRange +
        "&timeBin=" + chartSettings.timeBin +
        "&averageWindow=" + chartSettings.averageWindow;
    const result = useData(query);
    if(result){
        const series = result['series'];
        const graphDataWithSyncedColors = syncColors(
            series,
            allSettings);
        const highchartsOptions = generateOptions(
            graphDataWithSyncedColors,
            chartSettings);
        return (
            <div>
                <ChartSettings
                    settingsID={props.settingsID}
                />
                <HighchartsReact
                    highcharts={Highcharts}
                    options={highchartsOptions}
                    ref={chartRef}
                    constructorType={'chart'}
                />
                <ChartExports
                    chartRef={chartRef}
                />
            </div>
        );
    }else{
        return null;
    }


}
//TODO: labels
function ChartSettings(props){
    const settings = useContext(GraphSettingsContext);
    const settingsForID = settings[props.settingsID];
    const dispatch = useContext(GraphSettingsDispatchContext)
    return(
        <div className={'graphSettingsNavBar'}>
            <FormControl sx={{m: 1,minWidth: 120}}>
                <InputLabel id='timeBinLabel'>Group By</InputLabel>
                <Select
                    labelId='timeBinLabel'
                    value={settingsForID.timeBin}
                    label='Time Bin'
                    onChange={(event) => {
                        dispatch({
                            type: 'setTimeBin',
                            key: props.settingsID,
                            timeBin: event.target.value
                        })
                    }}
                >
                    <MenuItem value={'year'}>Year</MenuItem>
                    <MenuItem value={'month'}>Month</MenuItem>
                    <MenuItem value={'day'}>Day</MenuItem>
                </Select>
            </FormControl>
            <FormControl sx={{m: 1,minWidth: 120}}>
                <InputLabel id='averageWindowLabel'>Smoothing</InputLabel>
                <Select
                    label="Smoothing"
                    value={settingsForID.averageWindow}
                    onChange={e => {
                        dispatch({
                            type: 'setAverageWindow',
                            key: props.settingsID,
                            averageWindow: e.target.value,
                        });
                    }}
                >
                    <MenuItem value={0}>0</MenuItem>
                    <MenuItem value={1}>1</MenuItem>
                    <MenuItem value={2}>2</MenuItem>
                    <MenuItem value={3}>3</MenuItem>
                    <MenuItem value={4}>4</MenuItem>
                    <MenuItem value={5}>5</MenuItem>
                    <MenuItem value={6}>6</MenuItem>
                    <MenuItem value={7}>7</MenuItem>
                    <MenuItem value={8}>8</MenuItem>
                    <MenuItem value={9}>9</MenuItem>
                    <MenuItem value={10}>10</MenuItem>
                    <MenuItem value={11}>20</MenuItem>
                    <MenuItem value={12}>30</MenuItem>
                    <MenuItem value={13}>40</MenuItem>
                    <MenuItem value={14}>50</MenuItem>
                </Select>
            </FormControl>
            <ToggleButton
                value="Exclude sporadic papers"
                selected={settingsForID.continuous}
                onChange={() => {
                    dispatch({
                        type: 'setContinuous',
                        key: props.settingsID,
                        continuous: !settingsForID.continuous,
                    })
                }}
                label='require continuous newspapers'
            >
                Exclude papers incomplete over range
            </ToggleButton>

        </div>

    )
}

function ChartExports(props){
    const chartRef = props.chartRef;
    const [csvData, setCSVData] = React.useState(null);

    function handleExportGraphCSVclick(){
        const chart = chartRef.current.chart;
        const data = chart.downloadCSV();
        console.log(data)
        setCSVData(data);
    }

    function handleExportGraphCSVclose(){
        setCSVData(null);
    }

    return(
        <div className={'graphExports'}>
            <SVGexport chartRef={props.chartRef}/>
            <CSVexport
                chartRef={props.chartRef}
                onExportGraphCSVclick={handleExportGraphCSVclick}
                csvData={csvData}
                onExportGraphCSVclose={handleExportGraphCSVclose}
            />
        </div>
    )
}

function SVGexport(props){
    return(
        <button
            className={'graphExportButton'}
            onClick={() => {
                props.chartRef.current.chart.exportChart({
                    type: 'image/svg+xml',
                    filename: 'graph',
                });
            }}
        >
            Export SVG
        </button>
    )
}

function CSVexport(props){
    if(props.csvData){
        console.log(props.csvData)
        props.onExportGraphCSVclose();
        return(
            <CSVDownload
                data={props.csvData}
                filename={'graph.csv'}
            />
        )
    }else{
        return(
            <button
                className={'graphExportButton'}
                onClick={props.onExportGraphCSVclick}
            >
                Export Chart CSV
            </button>
        )
    }
}

export default Chart;