function fetchSeries(ticketIDs, settings){
    return fetch(
        "/graphData?keys=" + ticketIDs +
        "&averageWindow=" + settings.averageWindow +
        "&timeBin=" + settings.timeBin +
        "&continuous=" + settings.continuous)
}

module.exports = fetchSeries()