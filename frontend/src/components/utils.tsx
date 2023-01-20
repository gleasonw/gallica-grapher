import { scaleLinear } from "d3-scale";
import { extent } from "d3-array";

export function generateXAxisOptionsForNumericScale(values: number[]) {
  const numericValues = values.map((value) => Number(value));
  const [linearDomainMin, linearDomainMax] = extent(numericValues);
  const linearScale = scaleLinear().domain([
    linearDomainMin || 0,
    linearDomainMax || 0,
  ]);

  return {
    domain: linearScale.domain(),
    scale: linearScale,
    type: "number" as const,
    ticks: linearScale.ticks(),
  };
}
