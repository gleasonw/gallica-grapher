import { Suspense } from "react";
import { LoadingProvider } from "./components/LoadingProvider";
import { Dashboard } from "./dashboard";

export default function GraphPage() {
  return (
    <LoadingProvider>
      <Suspense fallback={<div>Chargement...</div>}>
        <Dashboard />
      </Suspense>
    </LoadingProvider>
  );
}
