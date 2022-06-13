

function updateSeries(ticketIDs, settings){
    return fetch(
        "/graphData?keys=" + ticketIDs +
        "&averageWindow=" + settings.averageWindow +
        "&timeBin=" + settings.timeBin +
        "&continuous=" + settings.continuous
    )
    .then(res => res.json())
}

module.exports = updateSeries()