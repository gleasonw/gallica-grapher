"use client";

import React from "react";
import { $path } from "next-typesafe-url";
import { useRouter } from "next/navigation";

const LoadingResultsContext = React.createContext<{
  isLoading: boolean;
  navigate: (...args: Parameters<typeof $path>) => void;
} | null>(null);

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
    <div>
      <LoadingResultsContext.Provider
        value={{ isLoading: isPending, navigate }}
      >
        {children}
      </LoadingResultsContext.Provider>
    </div>
  );
}

export const useNavigateWithLoading = () => {
  const loadingContext = React.useContext(LoadingResultsContext);
  if (!loadingContext) {
    throw new Error("useNavigateWithLoading must be used within a Providers");
  }
  return loadingContext;
};
