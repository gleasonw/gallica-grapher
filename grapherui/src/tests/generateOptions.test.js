const generateOptions = require('../utils/generateOptions');
let testSettings = {timeBin: 'year'}
let testSeries = {
    '1234':
        {
            name: 'neat',
            data: [[1,2],[3,4]],
            color: 'red'
        }}

describe('generatedOptions', () => {
    test('generate year grouped options when timebin is year', () => {
        let options = generateOptions(testSeries, testSettings);
        expect(options.xAxis.type).toEqual('line');
        expect(options.plotOptions.line.marker.enabled).toEqual(false);
        expect(options.series[0].name).toEqual('neat');
        expect(options.series[0].data).toEqual([[1,2],[3,4]]);
        expect(options.series[0].color).toEqual('red');
    });
    test('generate month grouped options when timebin is month', () => {
        testSettings.timeBin = 'month';
        let options = generateOptions(testSeries, testSettings);
        expect(options.xAxis.type).toEqual('datetime');
        expect(options.xAxis.dateTimeLabelFormats.month).toEqual('%b');
        expect(options.xAxis.dateTimeLabelFormats.year).toEqual('%Y');
        expect(options.series[0].name).toEqual('neat');
        expect(options.series[0].data).toEqual([[1,2],[3,4]]);
        expect(options.series[0].color).toEqual('red');
    });
    test('generate day grouped options when timebin is day', () => {
        testSettings.timeBin = 'day';
        let options = generateOptions(testSeries, testSettings);
        expect(options.xAxis.type).toEqual('datetime');
    });
} );