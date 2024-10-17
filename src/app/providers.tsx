"use client";

import React from "react";
import { $path } from "next-typesafe-url";
import { useRouter } from "next/navigation";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

const LoadingResultsContext = React.createContext<{
  isLoading: boolean;
  navigate: (...args: Parameters<typeof $path>) => void;
} | null>(null);

const queryClient = new QueryClient();

export function Providers({ children }: { children: React.ReactNode }) {
  const [isPending, startTransition] = React.useTransition();
  const router = useRouter();

  const navigate = React.useCallback(
    (...args: Parameters<typeof $path>) => {
      startTransition(() => router.push($path(...args)));
    },
    [router, startTransition]
  );

  return (
    <QueryClientProvider client={queryClient}>
      <LoadingResultsContext.Provider
        value={{ isLoading: isPending, navigate }}
      >
        {children}
      </LoadingResultsContext.Provider>
    </QueryClientProvider>
  );
}

export const useNavigateWithLoading = () => {
  const loadingContext = React.useContext(LoadingResultsContext);
  if (!loadingContext) {
    throw new Error("useNavigateWithLoading must be used within a Providers");
  }
  return loadingContext;
};
