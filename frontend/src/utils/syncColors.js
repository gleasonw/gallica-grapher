function syncColors(seriesToSync, settings) {
    return Object.keys(seriesToSync).map(key => (
        {
            ...seriesToSync[key],
            color: settings[key].color
        }
    ));
}

module.exports = syncColors;