

async function updateSeries(ticketIDs, settings){
    const data = fetch(
        "/graphData?keys=" + ticketIDs +
        "&averageWindow=" + settings.averageWindow +
        "&timeBin=" + settings.timeBin +
        "&continuous=" + settings.continuous
    )
    return await data.json();
}

module.exports = updateSeries()