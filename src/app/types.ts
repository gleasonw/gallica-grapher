import { components, paths } from "@/types";

export type VolumeRecord = components["schemas"]["VolumeRecord"];

export type Context = components["schemas"]["ContextRow"][];

export type Series = components["schemas"]["Series"];

export type ContextArgs =
  paths["/api/occurrences_no_context"]["get"]["parameters"]["query"];
