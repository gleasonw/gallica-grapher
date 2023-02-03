import { scaleLinear } from "d3-scale";
import { extent } from "d3-array";

export function generateXAxisOptionsForNumericScale(
  values: number[],
  refLeft: number | null,
  refRight: number | null
) {
  let linearDomainMin: number | undefined;
  let linearDomainMax: number | undefined;
  if (refLeft && refRight) {
    [linearDomainMin, linearDomainMax] = [refLeft, refRight];
  } else {
    // use the full extent of the data
    const numericValues = values.map((value) => Number(value));
    [linearDomainMin, linearDomainMax] = extent(numericValues);
  }
  const linearScale = scaleLinear().domain([
    linearDomainMin || 0,
    linearDomainMax || 0,
  ]);
  console.log(linearScale.domain());

  return {
    domain: linearScale.domain(),
    scale: linearScale,
    type: "number" as const,
    ticks: linearScale.ticks(),
  };
}
