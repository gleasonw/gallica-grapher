"use client";

import { usePathname, useRouter } from "next/navigation";
import React, { useCallback, useTransition } from "react";
import { useSearchState } from "../composables/useSearchState";
import { addQueryParamsIfExist } from "../utils/addQueryParamsIfExist";
import { SearchState } from "../utils/searchState";
import { GraphState } from "../utils/getGraphStateFromURL";

export type URLState = SearchState & GraphState;

const LoadingContext = React.createContext<{
  handleSubmit: (params: URLState) => void;
  isPending: boolean;
} | null>(null);

export function useSubmit() {
  const context = React.useContext(LoadingContext);
  if (!context) {
    throw new Error("useSubmit must be used within a LoadingProvider");
  }
  return context;
}

export function LoadingProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const path = usePathname();
  const [isPending, startTransition] = useTransition();
  const searchState = useSearchState();

  const handleSubmit = useCallback(
    (localParams: URLState) => {
      const url = addQueryParamsIfExist(path, {
        ...searchState,
        ...localParams,
      });
      startTransition(() => router.push(url, { scroll: false }));
    },
    [path, router, searchState, startTransition]
  );

  return (
    <LoadingContext.Provider value={{ handleSubmit, isPending }}>
      {children}
    </LoadingContext.Provider>
  );
}
