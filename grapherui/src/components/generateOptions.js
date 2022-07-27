
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