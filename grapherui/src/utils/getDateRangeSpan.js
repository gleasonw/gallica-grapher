function getDateRangeSpan(tickets) {
    if(Object.keys(tickets).length === 1) {
        return tickets[Object.keys(tickets)[0]].dateRange;
    }else{
        let lowestDate = Number.MAX_SAFE_INTEGER;
        let highestDate = Number.MIN_SAFE_INTEGER;
        Object.entries(tickets).forEach(([key, ticket]) => {
            if(ticket.dateRange[0] < lowestDate) {
                lowestDate = ticket.dateRange[0];
            }
            if(ticket.dateRange[1] > highestDate) {
                highestDate = ticket.dateRange[1];
            }
        });
        return [0, 2020];
    }

}

module.exports = getDateRangeSpan;