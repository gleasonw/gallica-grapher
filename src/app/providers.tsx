"use client";

import React from "react";
import { QueryClient, QueryClientProvider } from "react-query";

export interface ProvidersProps {
  children?: React.ReactNode;
}

export function Providers({ children }: ProvidersProps) {
  const queryClient = React.useMemo(() => new QueryClient(), []);
  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}
