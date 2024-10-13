"use client";

import { useNavigateWithLoading } from "@/src/app/providers";

export function SkeletonsWhenLoading({
  loadedUI,
}: {
  loadedUI: React.ReactElement;
}) {
  const { isLoading } = useNavigateWithLoading();
  if (isLoading) {
    return Array.from({ length: 5 }).map(() => (
      <div className="h-44 w-full animate-pulse bg-gray-200 rounded-md"></div>
    ));
  }

  return loadedUI;
}
