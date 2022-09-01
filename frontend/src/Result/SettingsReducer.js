export function settingsReducer(graphSettings, action) {
    switch (action.type) {
        case 'setSeries' : {
            return {
                ...graphSettings,
                [action.key]: {
                    ...graphSettings[action.key],
                    series: action.series
                }
            }
        }
        case 'setTimeBin': {
            if (action.timeBin) {
                return {
                    ...graphSettings,
                    [action.key]: {
                        ...graphSettings[action.key],
                        timeBin: action.timeBin,
                    }
                }
            } else {
                return graphSettings
            }
        }
        case 'setAverageWindow': {
            return {
                ...graphSettings,
                [action.key]: {
                    ...graphSettings[action.key],
                    averageWindow: action.averageWindow ?
                        action.averageWindow : 0,
                }
            }
        }
        case 'setContinuous': {
            return {
                ...graphSettings,
                [action.key]: {
                    ...graphSettings[action.key],
                    continuous: action.continuous,
                }
            }
        }
        case 'setTicketSettings': {
            return {
                ...graphSettings,
                [action.key]: action.settings
            }
        }
        case 'setColor': {
            return {
                ...graphSettings,
                [action.key]: {
                    ...graphSettings[action.key],
                    color: action.color
                }
            }
        }
        default:
            throw Error("Unknown action: " + action.type);
    }
}