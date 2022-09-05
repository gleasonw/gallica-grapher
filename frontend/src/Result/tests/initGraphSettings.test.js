import initGraphSettingsTest from '../chartUtils/initGraphSettings';

describe('The function that initializes graph settings', () => {
    const testTickets = {
        '1234': {},
        '5678': {},
        '9012': {}
    }
    it('should initialize the default settings for each ticket and add a group setting', () => {
        expect(initGraphSettingsTest(testTickets)).toEqual({
            '1234': {
                color: '#7cb5ec',
                timeBin: 'year',
                averageWindow: '0',
                continuous: false
            },
            '5678': {
                color: '#434348',
                timeBin: 'year',
                averageWindow: '0',
                continuous: false
            },
            '9012': {
                color: '#90ed7d',
                timeBin: 'year',
                averageWindow: '0',
                continuous: false
            },
            'group': {
                timeBin: 'year',
                averageWindow: '0',
                continuous: false
            }
        });
    });
    it('should repeat first color with more than 10 tickets', () => {
        const testTickets = {
            '1': {},
            '2': {},
            '3': {},
            '4': {},
            '5': {},
            '6': {},
            '7': {},
            '8': {},
            '9': {},
            '99': {},
            '999': {}
        }
        const testSettings = initGraphSettingsTest(testTickets);
        expect(testSettings['999'].color).toEqual('#7cb5ec');
    });
});