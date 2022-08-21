export function getWidestDateRange(tickets) {
    let widestDateRange = 0;
    let widestTicket = null;
    Object.keys(tickets).forEach(key => {
        const lowYear = tickets[key].dateRange[0];
        const highYear = tickets[key].dateRange[1];
        const thisWidth = highYear - lowYear;
        if (thisWidth > widestDateRange) {
            widestDateRange = thisWidth;
            widestTicket = key;
        }
    });
    return tickets[widestTicket].dateRange;
}