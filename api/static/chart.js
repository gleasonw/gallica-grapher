var url = $(location).attr('href');
var urlParts = url.split("/")
var threadId = urlParts[urlParts.length - 1]


$(document).ready(function () {
    const displayChart = async () => {
        const fetchedGraphJSON = await getGraphJSON()
        let dateRange = fetchedGraphJSON["dateRange"]
        let data = fetchedGraphJSON["data"]
        console.log(data)
        let terms = fetchedGraphJSON["terms"]
        $.each(data, function(index, dataGroup){
            data[index] = JSON.parse(data[index])
        })
        console.log(data)
        $("#chart").highcharts('StockChart',{
            plotOptions: {
                series: {
                    type: 'bar'
                }
            },
            chart: {
                zoomType: 'x'
            },
            title: {
                text: "Usage of '{0}' from {1}".format(terms, dateRange)
            },

            xAxis: {
                type: 'datetime'
            },

            yAxis: {
                title: {
                    text: 'Mentions'
                }
            },
            legend: {
                enabled: true
            },
            series: data
        });
    };
    displayChart();
});


const getGraphJSON = async () => {
    const graphJSONResponse = await fetch('/results/{0}/graphData'.format(threadId));
    return await graphJSONResponse.json()
};

String.prototype.format = String.prototype.f = function() {
    var s = this,
        i = arguments.length;

    while (i--) {
        s = s.replace(new RegExp('\\{' + i + '\\}', 'gm'), arguments[i]);
    }
    return s;
};
