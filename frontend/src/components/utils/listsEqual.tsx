export default function listsEqual<T>(a: T[], b: T[]): boolean {
  const aNoUndefined = a.filter((x) => x !== undefined);
  const bNoUndefined = b.filter((x) => x !== undefined);
  const aSort = aNoUndefined.sort();
  const bSort = bNoUndefined.sort();
  if (aNoUndefined.length !== bNoUndefined.length) {
    return false;
  }
  for (let i = 0; i < aSort.length; i++) {
    const item = aSort[i];
    if (Array.isArray(item)) {
      if (!listsEqual(item, bSort[i])) {
        console.log(item);
        return false;
      }
    } else if (aSort[i] !== bSort[i]) {
      return false;
    }
  }
  return true;
}
