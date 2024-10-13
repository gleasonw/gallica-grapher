"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useNavigateWithLoading } from "@/src/app/providers";
import { Route, SearchParams } from "@/src/app/routeType";
import { Search } from "lucide-react";
import { $path } from "next-typesafe-url";
import { useSearchParams } from "next-typesafe-url/app";
import Link from "next/link";
import React from "react";

export function TermSearchInput() {
  const [searchTerm, setSearchTerm] = React.useState("");
  const { data } = useSearchParams(Route.searchParams);
  const { navigate, isLoading } = useNavigateWithLoading();

  return (
    <div className="flex relative items-center gap-3">
      <Input
        className="w-full pl-10 pr-4 py-6 text-lg shadow-lg"
        placeholder={data?.terms ? data.terms[0] : "Search for a term..."}
        value={searchTerm}
        onChange={(e) => {
          setSearchTerm(e.target.value);
        }}
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            navigate({ route: "/", searchParams: { terms: searchTerm } });
          }
        }}
      />
      <div className="flex items-center gap-2">
        <Input className="text-xs w-3/4" placeholder="Link term" />
        <Input className="text-xs w-1/4" placeholder="Distance" />
      </div>

      <Button
        size="lg"
        className="px-8 shadow-lg"
        onClick={() =>
          navigate({ route: "/", searchParams: { terms: searchTerm } })
        }
      >
        {isLoading ? "Searching..." : "Search"}
      </Button>
      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
    </div>
  );
}

export function YearInput({ params }: { params: SearchParams }) {
  const [localStart, setLocalStart] = React.useState<string | null>(null);
  const [localEnd, setLocalEnd] = React.useState<string | null>(null);

  const parsedStartYear = localStart ? parseInt(localStart) : null;
  const parsedEndYear = localEnd ? parseInt(localEnd) : null;

  const { navigate } = useNavigateWithLoading();

  return (
    <div className="relative">
      <div className="flex gap-2 p-2 items-center">
        <Input
          placeholder={params.year?.toString() ?? "Start year"}
          value={localStart ?? undefined}
          onChange={(e) => setLocalStart(e.target.value)}
          className="border-0"
        />
        <Input
          placeholder={params.end_year?.toString() ?? "End year"}
          value={localEnd ?? undefined}
          onChange={(e) => setLocalEnd(e.target.value)}
          className="border-0"
        />
        <Link
          href={$path({
            route: "/",
            searchParams: {
              ...params,
              year: parsedStartYear ?? params.year,
              end_year: parsedEndYear ?? params.end_year,
            },
          })}
        >
          <Button variant="outline">Apply</Button>
        </Link>
      </div>
      <div className="absolute bottom-0 bg-white z-10 translate-y-full">
        {parsedStartYear !== null && isNaN(parsedStartYear) ? (
          <div>Start year must be a number</div>
        ) : null}
        {parsedEndYear !== null && isNaN(parsedEndYear) ? (
          <div>End year must be a number</div>
        ) : null}
      </div>
    </div>
  );
}
