export default function allAinB(a: any, b: any): boolean {
  if (!a || !b) return false;
  return Object.keys(a).every((key) => {
    const item = a[key];
    if (Array.isArray(item)) {
      return item.every((item, index) => {
        return item === b[key]?.[index];
      });
    }
    return a[key] === b[key];
  });
}
