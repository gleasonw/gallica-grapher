export default function currentParamObjectEqualsInitial(
  currentParams: any,
  initialParams: any
): boolean {
  if(!currentParams || !initialParams) return false;
  return Object.keys(currentParams).every((key) => {
    const item = currentParams[key];
    if (Array.isArray(item)) {
      return item.every((item, index) => {
        return item === initialParams[key][index];
      });
    }
    return currentParams[key] === initialParams[key];
  });
}
