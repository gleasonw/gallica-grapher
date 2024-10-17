import { redirect } from "next/navigation";

export default function OldContextPage({
  searchParams,
}: {
  searchParams: Record<string, any>;
}) {
  const queryString = new URLSearchParams(searchParams).toString();
  redirect(`/?${queryString}`);
}
