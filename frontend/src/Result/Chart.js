import HighchartsReact from "highcharts-react-official";
import Highcharts from "highcharts";
import styled from 'styled-components';
import React, {useContext, useRef} from "react";
import {GraphSettingsContext, GraphSettingsDispatchContext} from "./GraphSettingsContext";
import useData from "../shared/hooks/useData";
import syncColors from "./chartUtils/syncColors";
import generateOptions from "./chartUtils/generateOptions";
import getDateRangeSpan from "./chartUtils/getDateRangeSpan";
import NavBarWrap from "./NavBarWrap";
import {StyledSelect} from "../shared/StyledSelect";
import {StyledInputAndLabel} from "../shared/StyledSelect";

require("highcharts/modules/exporting")(Highcharts);
require("highcharts/modules/export-data")(Highcharts);

function Chart(props) {
    const allSettings = useContext(GraphSettingsContext)
    const chartSettings = allSettings[props.settingsID];
    const dateRange = getDateRangeSpan(props.tickets);
    const startYear = dateRange[0];
    const endYear = dateRange[1];
    const chartRef = useRef(null);
    const query =
        "/api/graphData?keys=" + Object.keys(props.tickets) +
        "&requestID=" + props.requestID +
        "&continuous=" + chartSettings.continuous +
        "&startYear=" + startYear +
        "&endYear=" + endYear +
        "&timeBin=" + chartSettings.timeBin +
        "&averageWindow=" + chartSettings.averageWindow +
        "&uniqueforcache=" + props.uuid;
    const result = useData(query);
    if (result) {
        const series = result['series'];
        const graphDataWithSyncedColors = syncColors(
            series,
            allSettings);
        const highchartsOptions = generateOptions(
            graphDataWithSyncedColors,
            chartSettings,
            props.onSeriesClick
        );
        return (
            <StyledChartUI>
                <ChartSettings
                    settingsID={props.settingsID}
                />
                <HighchartsReact
                    highcharts={Highcharts}
                    options={highchartsOptions}
                    ref={chartRef}
                    constructorType={'chart'}
                />
            </StyledChartUI>
        );
    } else {
        return null;
    }
}

const StyledChartUI = styled.div`
    display: flex;
    flex-direction: column;
    margin-top: 20px;
`;

function ChartSettings(props) {
    const settings = useContext(GraphSettingsContext);
    const settingsForID = settings[props.settingsID];
    const dispatch = useContext(GraphSettingsDispatchContext)
    const isGallicaGrouped = settingsForID.timeBin === "gallicaYear" || settingsForID.timeBin === "gallicaMonth";
    return (
        <NavBarWrap>
            <StyledInputAndLabel display={isGallicaGrouped ? 'none' : 'flex'}>
                <label htmlFor='timeBin'>Group by</label>
                <StyledSelect
                    id='timeBin'
                    value={settingsForID.timeBin}
                    onChange={(event) => {
                        dispatch({
                            type: 'setTimeBin',
                            key: props.settingsID,
                            timeBin: event.target.value
                        })
                    }}
                >
                    <option value={'year'}>Year</option>
                    <option value={'month'}>Month</option>
                    <option value={'day'}>Day</option>
                </StyledSelect>
            </StyledInputAndLabel>
            <StyledInputAndLabel>
                <label htmlFor='averageWindow'>Smoothing</label>
                <StyledSelect
                    id='averageWindow'
                    value={settingsForID.averageWindow}
                    onChange={e => {
                        dispatch({
                            type: 'setAverageWindow',
                            key: props.settingsID,
                            averageWindow: e.target.value,
                        });
                    }}
                >
                    <option value={0}>0</option>
                    <option value={1}>1</option>
                    <option value={2}>2</option>
                    <option value={3}>3</option>
                    <option value={4}>4</option>
                    <option value={5}>5</option>
                    <option value={6}>6</option>
                    <option value={7}>7</option>
                    <option value={8}>8</option>
                    <option value={9}>9</option>
                    <option value={10}>10</option>
                    <option value={11}>20</option>
                    <option value={12}>30</option>
                    <option value={13}>40</option>
                    <option value={14}>50</option>
                </StyledSelect>
            </StyledInputAndLabel>
            <StyledInputAndLabel display={isGallicaGrouped ? 'none' : 'flex'}>
                <label htmlFor='continuous'>Only continuous periodicals publishing over range</label>
                <input
                    id='continuous'
                    type='checkbox'
                    checked={settingsForID.continuous}
                    onChange={e => {
                        dispatch({
                            type: 'setContinuous',
                            key: props.settingsID,
                            continuous: e.target.checked,
                        });
                    }}
                />
            </StyledInputAndLabel>
        </NavBarWrap>
    )
}

export default Chart;