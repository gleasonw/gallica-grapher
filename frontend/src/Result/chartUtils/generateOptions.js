export default function generateOptions(series, settings, onSeriesClick, from_pyllicagram) {
    let options = {
        chart: {
            type: 'line',
            zoomType: 'x',
            panning: true,
            panKey: 'shift'
        },
        plotOptions:{
            series: {
                cursor: 'pointer',
                point: {
                  events: {
                    click: (e) => onSeriesClick(e.point)
                  }
                }
              }
        },
        legend: {
            dateTimeLabelFormats: {
                month: '%b',
                year: '%Y'
            },
            align: 'left',
            verticalAlign: 'top',
            borderWidth: 0,
            itemStyle: {
                fontSize: '15px',
            }
        },
        title: {
            text: null
        },
        yAxis: {
            title: {
                text: from_pyllicagram ? 'occurrences / total words in period' : 'volumes with at least one occurrence'
            }
        },
        series: series,
        tooltip: {
            shared: true,
            crosshairs: true,
        },
    };
    if (settings.timeBin === 'year' || settings.timeBin === 'gallicaYear') {
        formatYearOptions()
    } else if (settings.timeBin === 'month' || settings.timeBin === 'gallicaMonth') {
        formatYearMonOptions()
    } else {
        formatYearMonDayOptions()
    }

    function formatYearOptions() {
        options.plotOptions = {
            ...options.plotOptions,
            line: {
                marker: {
                    enabled: false
                }
            }
        }
        options.xAxis = {
            type: 'line',
        }
    }

    function formatYearMonOptions() {
        options.xAxis = {
            type: 'datetime',
            dateTimeLabelFormats: {
                month: '%b',
                year: '%Y'
            }
        }
    }

    function formatYearMonDayOptions() {
        options.xAxis = {type: 'datetime'}
    }

    return options;
}
