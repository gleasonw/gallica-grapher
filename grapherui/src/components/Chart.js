import HighchartsReact from "highcharts-react-official";
import Highcharts from "highcharts";
import React from "react";
import TextField from '@mui/material/TextField';
import ToggleButton from '@mui/material/ToggleButton';
import ToggleButtonGroup from '@mui/material/ToggleButtonGroup';

function Chart(props) {
    const JSONoptions = props.options
    return (
        <div>
            <HighchartsReact
                highcharts={Highcharts}
                options={JSONoptions}
            />
            <ChartOptions/>
        </div>


    );
}
function ChartOptions(props){
    const [alignment, setAlignment] = React.useState('left');

    const handleAlignment = (event, newAlignment) => {
    setAlignment(newAlignment);
    };
    return(
        <div>
            <ToggleButtonGroup
              value={alignment}
              exclusive
              onChange={handleAlignment}
              aria-label="text alignment"
            >
              <ToggleButton value="left" aria-label="year-grouped">
              </ToggleButton>
              <ToggleButton value="center" aria-label="mon-grouped">
              </ToggleButton>
              <ToggleButton value="right" aria-label="day-grouped">
              </ToggleButton>
            </ToggleButtonGroup>
            <TextField/>

        </div>

    )
}

export default Chart;