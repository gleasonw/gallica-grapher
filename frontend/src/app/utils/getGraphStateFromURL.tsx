import { z } from "zod";

export const graphState = z.object({
  grouping: z.literal("year").or(z.literal("month")).optional(),
  smoothing: z.number().optional(),
});

export type GraphState = z.infer<typeof graphState>;

export function getGraphStateFromURL(params: Record<string, any>): {
  graphState?: z.infer<typeof graphState>;
  error?: string;
} {
  const result = graphState.safeParse(params);
  if (!result.success) {
    return { error: result.error.message };
  }
  return { graphState: result.data };
}
