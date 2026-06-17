/**
 * Central query-key factory so cache invalidation stays consistent across hooks
 * (added in the data-layer prompt). Keys are arrays, namespaced by domain.
 */
export const queryKeys = {
  links: {
    all: ["links"] as const,
    list: (params: { limit: number; offset: number }) =>
      ["links", "list", params] as const,
  },
  stats: {
    all: ["stats"] as const,
    detail: (shortCode: string) => ["stats", shortCode] as const,
  },
} as const;
