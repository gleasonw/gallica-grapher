"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Home } from "./Home";

export function App() {
  const client = new QueryClient();
  return (
    <QueryClientProvider client={client}>
      <Home />
    </QueryClientProvider>
  );
}
