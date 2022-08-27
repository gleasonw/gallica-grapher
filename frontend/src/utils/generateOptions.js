export default function generateOptions(series, settings) {
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
    if (settings.timeBin === 'year') {
        formatYearOptions()
    } else if (settings.timeBin === 'month') {
        formatYearMonOptions()
    } else {
        formatYearMonDayOptions()
    }

    function formatYearOptions() {
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