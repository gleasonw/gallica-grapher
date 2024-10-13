"use client";

export function NumberRecords({ records }: { records: number }) {
  return <>{Intl.NumberFormat(navigator.language).format(records)} records</>;
}
