import { useSearchParams } from "next/navigation";
import { getGraphStateFromURL } from "../utils/getGraphStateFromURL";

export function useGraphState() {
  const currentParams = useSearchParams();
  return getGraphStateFromURL(currentParams);
}
