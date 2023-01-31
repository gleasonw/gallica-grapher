import { router } from "../trpc";

// moved most fetching code to the client, keeping the trpc router for now
export const appRouter = router({});

// export type definition of API
export type AppRouter = typeof appRouter;
