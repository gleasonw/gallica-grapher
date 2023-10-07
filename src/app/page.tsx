import Chart from "./components/Chart";
import { LoadingProvider } from "./components/LoadingProvider";
import { Dashboard } from "./dashboard";

export default function GraphPage({
  searchParams,
}: {
  searchParams: Record<string, string>;
}) {
  return (
    <LoadingProvider>
      <Dashboard serverChartComponent={<Chart searchParams={searchParams} />} />
    </LoadingProvider>
  );
}
