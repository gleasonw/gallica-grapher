import HighchartsReact from "highcharts-react-official";
import Highcharts from "highcharts";
import React from "react";

export function Chart(props) {
    const JSONoptions = props.options
    return (
        <HighchartsReact
            highcharts={Highcharts}
            options={JSONoptions}
        />
    );
}

export default Chart;