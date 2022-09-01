const getWidestDateRangeTest = require('../Result/chartUtils/getDateRangeSpan');

describe('The date range span function', () => {
    it('returns the lowest and highest dates out of many tickets', () => {
        const testTickets = {
            '1234': {
                dateRange: [1, 2],
            },
            '5678': {
                dateRange: [3, 4],
            },
            '9012': {
                dateRange: [0,100]
            },
            '3456': {
                dateRange: [1499, 2020]
            }
        }
        expect(getWidestDateRangeTest(testTickets)).toEqual([0, 2020]);
    });
    it('bounces a lone ticket', () => {
        const testTickets = {
            '1234': {
                dateRange: [1, 2],
            }
        }
        expect(getWidestDateRangeTest(testTickets)).toEqual([1, 2]);
    });
});
