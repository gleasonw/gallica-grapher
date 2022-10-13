export default function initGraphSettings(tickets) {
    const highChartsSeriesColors = [
        '#7cb5ec',
        '#434348',
        '#90ed7d',
        '#f7a35c',
        '#8085e9',
        '#f15c80',
        '#e4d354',
        '#2b908f',
        '#f45b5b',
        '#91e8e1'];
    let indexForColorAssignment = 0;
    const initSetting = {
        averageWindow: '0',
        continuous: false
    }
    let initialGraphSettings = {}
    for (let key in tickets) {
        initialGraphSettings[key] = {
            ...initSetting,
            timeBin: getTimeBinForSearchType(tickets[key].searchType),
            color: highChartsSeriesColors[indexForColorAssignment]
        }
        indexForColorAssignment =
            (indexForColorAssignment + 1) %
            highChartsSeriesColors.length;
    }
    initialGraphSettings["group"] = initSetting;
    return initialGraphSettings
}

function getTimeBinForSearchType(searchType) {
    const timeBins = {
        'all': 'year',
        'year': 'gallicaYear',
        'month': 'gallicaMonth'
    }
    return timeBins[searchType]
}