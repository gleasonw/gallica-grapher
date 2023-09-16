import { useSearchState } from "./useSearchState";

export function useSelectedTerm(): string {
  const { terms, selected_term } = useSearchState();
  return selected_term ?? terms?.[0] ?? "brazza";
}
