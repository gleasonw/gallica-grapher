import { z } from "zod";

export const graphState = z.object({
  grouping: z.literal("annee").or(z.literal("mois")).optional(),
  smoothing: z.number().optional(),
});

export type GraphState = z.infer<typeof graphState>;

export function getGraphStateFromURL(params: Record<string, any>) {
  const result = graphState.safeParse(params);
  if (!result.success) {
    return {};
  }
  return result.data;
}
