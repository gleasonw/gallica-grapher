const genOptions = require('../generateOptions');

test("Generates Highcharts options for a year-binned series", () => {
    expect(genOptions('year',[])).toMatchObject({
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
        series: [],
        plotOptions: {
            line: {
                marker: {
                    enabled: false
                }
            }
        },
        xAxis: {
            type: 'line'
        }
    }
    )
})
test("Generates Highcharts options for a month-binned series", () => {
    expect(genOptions('month',[])).toMatchObject({
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
        series: [],
        xAxis: {
            type: 'datetime',
            dateTimeLabelFormats: {
                month: '%b',
                year: '%Y'
            }
        }
    }
    )
})
test("Generates Highcharts options for a day-binned series", () => {
    expect(genOptions('day',[])).toMatchObject({
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
        series: [],
        xAxis: { type: 'datetime'}
    }
    )
})