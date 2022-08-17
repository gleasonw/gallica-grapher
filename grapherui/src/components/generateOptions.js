
function generateOptions(timeBin, series){
    if(series){
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
            colors: [
                '#7cb5ec',
                '#434348',
                '#90ed7d',
                '#f7a35c',
                '#8085e9',
                '#f15c80',
                '#e4d354',
                '#2b908f',
                '#f45b5b',
                '#91e8e1'
            ],
            series: Object.values(series)
        }
        if(timeBin === 'year'){
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
        }else if(timeBin === 'month'){
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
}

module.exports = generateOptions;