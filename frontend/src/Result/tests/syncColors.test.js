import syncColorsTest from '../chartUtils/syncColors';

describe('The function that syncs user color settings with a highcharts series', () => {
    it('should add the color of a ticket to its series', () => {
        const testSeriesNoColor = {'1234': {name: 'neat', data: [[1,2],[3,4]]}};
        const testSettings = {'1234': {color: 'red'}};
        const testSeriesWithColor = syncColorsTest(testSeriesNoColor, testSettings);
        expect(testSeriesWithColor[0].color).toEqual('red');
    });
    it('should add the colors of multiple tickets to their series', () => {
        const testSeriesNoColor = {
            '1234': {name: 'neat', data: [[1,2],[3,4]]},
            '5678': {name: 'banana', data: [[1,2],[3,4]]}
        };
        const testSettings = {
            '1234': {color: 'red'},
            '5678': {color: 'blue'}
        };
        const testSeriesWithColor = syncColorsTest(testSeriesNoColor, testSettings);
        expect(testSeriesWithColor.find(series => series.name === 'neat').color).toEqual('red');
        expect(testSeriesWithColor.find(series => series.name === 'banana').color).toEqual('blue');
    });
});