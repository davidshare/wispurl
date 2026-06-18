import { QueryCache, QueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { ApiError } from "@/lib/api/error";

/**
 * Create a QueryClient with app defaults plus GLOBAL handling for the two failure
 * modes worth a friendly, actionable message: rate limiting (429) and server
 * errors (5xx). Component-level mutation handlers cover their own specifics.
 */
export function makeQueryClient(): QueryClient {
  return new QueryClient({
    queryCache: new QueryCache({
      onError: (error) => {
        if (!(error instanceof ApiError)) return;
        if (error.status === 429) {
          toast.error(
            "You're going a bit fast — wait a few seconds, then try again.",
          );
        } else if (error.status >= 500) {
          toast.error("Something's off on our end. Please try again in a moment.");
        }
      },
    }),
    defaultOptions: {
      queries: {
        // Access tokens live 15 min; keep data fresh-ish but avoid refetch storms.
        staleTime: 30_000,
        gcTime: 5 * 60_000,
        retry: 1,
        refetchOnWindowFocus: false,
      },
    },
  });
}
