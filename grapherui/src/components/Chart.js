import HighchartsReact from "highcharts-react-official";
import Highcharts from "highcharts";
import React from "react";
import TextField from '@mui/material/TextField';
import ToggleButton from '@mui/material/ToggleButton';
import ToggleButtonGroup from '@mui/material/ToggleButtonGroup';
import Button from '@mui/material/Button'

function Chart(props) {
    return (
        <div>
            <HighchartsReact
                highcharts={Highcharts}
                options={props.options}
            />
            <ChartOptions
                timeBinVal={props.timeBinVal}
                averageWindow={props.averageWindow}
                onChange={props.onChange}
            />
        </div>


    );
}
function ChartOptions(props){
    return(
        <div>
            <ToggleButtonGroup
              value={props.timeBinVal}
              exclusive
              onChange={props.onChange}
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
                onChange={props.onChange}
                name='averageWindow'
                label='Rolling average'
                type='number'
            />

            <Button variant="text">
                Download PNG
            </Button>

        </div>

    )
}

export default Chart;