import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import { queryKeys } from "@/lib/query/query-keys";
import type { Link, LinkList } from "@/lib/api/types";

export interface CreateLinkInput {
  long_url: string;
  custom_slug?: string;
  expires_at?: string;
}

/** Paginated list of the current user's links. */
export function useLinks(params: { limit: number; offset: number }) {
  return useQuery({
    queryKey: queryKeys.links.list(params),
    queryFn: () =>
      apiFetch<LinkList>(`/links?limit=${params.limit}&offset=${params.offset}`),
  });
}

interface MutationContext {
  previous: [readonly unknown[], LinkList | undefined][];
  tempId: string;
}

/**
 * Create a link with an OPTIMISTIC insert into every cached links list: the new row
 * appears immediately, is replaced with the server row on success, and is rolled
 * back if the request fails (e.g. a slug collision or rate limit). Toasts and
 * field-level errors are handled by the calling component.
 */
export function useCreateLink() {
  const queryClient = useQueryClient();

  return useMutation<Link, Error, CreateLinkInput, MutationContext>({
    mutationFn: (input) =>
      apiFetch<Link>("/links", { method: "POST", json: input }),

    onMutate: async (input) => {
      await queryClient.cancelQueries({ queryKey: queryKeys.links.all });
      const previous = queryClient.getQueriesData<LinkList>({
        queryKey: queryKeys.links.all,
      });
      const tempId = `optimistic-${crypto.randomUUID()}`;
      const optimistic: Link = {
        id: tempId,
        short_code: input.custom_slug ?? "…",
        long_url: input.long_url,
        short_url: "",
        created_at: new Date().toISOString(),
        expires_at: input.expires_at ?? null,
        is_active: true,
      };
      queryClient.setQueriesData<LinkList>(
        { queryKey: queryKeys.links.all },
        (old) =>
          old
            ? { ...old, items: [optimistic, ...old.items], total: old.total + 1 }
            : old,
      );
      return { previous, tempId };
    },

    onError: (_error, _input, context) => {
      // Roll the optimistic insert back to the pre-mutation snapshots.
      context?.previous.forEach(([key, data]) => {
        queryClient.setQueryData(key, data);
      });
    },

    onSuccess: (link, _input, context) => {
      // Swap the optimistic row for the real one (no refetch needed).
      queryClient.setQueriesData<LinkList>(
        { queryKey: queryKeys.links.all },
        (old) =>
          old
            ? {
                ...old,
                items: old.items.map((item) =>
                  item.id === context.tempId ? link : item,
                ),
              }
            : old,
      );
    },
  });
}
