import { useSearchParams } from "next/navigation";
import { getGraphStateFromURL } from "../utils/getGraphStateFromURL";

export function useGraphState() {
  const currentParams = useSearchParams();
  const paramsObject: { [key: string]: string | string[] } = {};
  currentParams.forEach((value, key) => {
    const item = paramsObject[key];
    if (item) {
      if (Array.isArray(item)) {
        item.push(value);
      } else {
        paramsObject[key] = [item, value];
      }
    } else {
      paramsObject[key] = value;
    }
  });
  return getGraphStateFromURL(paramsObject);
}
