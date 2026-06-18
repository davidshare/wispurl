import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { API_PREFIX } from "@/lib/env";
import { queryKeys } from "@/lib/query/query-keys";
import type { Stats } from "@/lib/api/types";

/** Query options for one short code's stats — reusable in useQuery and useQueries. */
export function statsQueryOptions(shortCode: string) {
  return {
    queryKey: queryKeys.stats.detail(shortCode),
    queryFn: () => apiFetch<Stats>(`${API_PREFIX}/stats/${shortCode}`),
  };
}

/** Aggregated stats for a single short code. */
export function useStats(shortCode: string) {
  return useQuery(statsQueryOptions(shortCode));
}
