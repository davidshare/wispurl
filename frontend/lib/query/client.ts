import { QueryClient } from "@tanstack/react-query";

/**
 * Create a QueryClient with app defaults. A factory (not a singleton) so the
 * browser and each SSR render get their own client, per TanStack guidance.
 */
export function makeQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        // Access tokens live 15 min; keep data fresh-ish but avoid refetch storms.
        staleTime: 30_000,
        retry: 1,
        refetchOnWindowFocus: false,
      },
    },
  });
}
