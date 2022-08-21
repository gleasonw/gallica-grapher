export function syncColors(seriesToSync, settings, tickets) {
    const keyColorPairs = Object.keys(tickets).map(key => {
        return {
            key: key,
            color: settings[key].color
        }
    });
    return seriesToSync.map(key => {
        const color = keyColorPairs.find(pair => pair.key === key.key).color;
        return {
            ...seriesToSync[key],
            color: color
        }
    });
}