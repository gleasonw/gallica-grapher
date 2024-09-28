import React, { Suspense } from "react";
import { getSearchStateFromURL } from "../utils/searchState";
import { ClientContextFetch } from "./client-fetch-context";

export default async function Page({
  searchParams,
}: {
  searchParams: Record<string, any>;
}) {
  const params = getSearchStateFromURL(searchParams);

  return (
    <Suspense
      fallback={<div className="flex w-full justify-center">Chargement...</div>}
    >
      <ClientContextFetch fetchParams={params} />
    </Suspense>
  );
}
