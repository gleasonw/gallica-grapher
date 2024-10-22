"use client";

export function NumberRecords({ records }: { records: number }) {
  if (typeof window === "undefined") {
    return null;
  }
  return <>{Intl.NumberFormat(navigator.language).format(records)} résultats</>;
}
