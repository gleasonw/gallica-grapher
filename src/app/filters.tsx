// Site en français

"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Popover,
  PopoverTrigger,
  PopoverContent,
} from "@/components/ui/popover";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useNavigateWithLoading } from "@/src/app/providers";
import { Route, SearchParams } from "@/src/app/routeType";
import { Filter, Link, X } from "lucide-react";
import { useSearchParams } from "next-typesafe-url/app";
import React from "react";

export function Filters() {
  const { data: params } = useSearchParams(Route.searchParams);
  const [filterState, setFilterState] = React.useState<
    | Pick<
        SearchParams,
        | "source"
        | "sort"
        | "year"
        | "end_year"
        | "cursor"
        | "link_distance"
        | "link_term"
      >
    | undefined
  >(params);
  const { year, end_year, source, sort, link_term, link_distance } =
    filterState ?? {};

  const { isLoading, navigate } = useNavigateWithLoading();
  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="outline" size="lg" className="shadow-lg">
          <Filter className="h-4 w-4 mr-2" />
          Filtres
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-80">
        <div className="space-y-4">
          <div className="flex items-center space-x-2">
            <Input
              id="startYear"
              type="number"
              min={1785}
              max={1945}
              value={year}
              onChange={(e) =>
                setFilterState({
                  ...filterState,
                  year: isNaN(e.target.valueAsNumber)
                    ? undefined
                    : e.target.valueAsNumber,
                })
              }
              placeholder={
                filterState?.year?.toString() ??
                params?.year?.toString() ??
                "Année de début"
              }
            />
            <Input
              id="endYear"
              type="number"
              min={1785}
              max={1945}
              value={end_year}
              onChange={(e) =>
                setFilterState({
                  ...filterState,
                  end_year: isNaN(e.target.valueAsNumber)
                    ? undefined
                    : e.target.valueAsNumber,
                })
              }
              placeholder={
                filterState?.end_year?.toString() ??
                params?.end_year?.toString() ??
                "Année de fin"
              }
            />
          </div>
          <Select
            value={source}
            onValueChange={(value) =>
              setFilterState({
                ...filterState,
                source: value as "all" | "book" | "periodical",
              })
            }
          >
            <SelectTrigger>
              <SelectValue placeholder="Source" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Tous</SelectItem>
              <SelectItem value="book">Livre</SelectItem>
              <SelectItem value="periodical">Périodique</SelectItem>
            </SelectContent>
          </Select>
          <Select
            value={sort}
            onValueChange={(value) =>
              setFilterState({
                ...filterState,
                sort: value as "date" | "relevance",
              })
            }
          >
            <SelectTrigger>
              <SelectValue placeholder="Tri" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="relevance">Pertinence</SelectItem>
              <SelectItem value="date">Date</SelectItem>
            </SelectContent>
          </Select>
          <div className="flex w-full justify-between items-center">
            <Link />
            <div className="flex gap-2 flex-col">
              <Input
                placeholder="Terme associé"
                value={link_term}
                onChange={(e) =>
                  setFilterState({
                    ...filterState,
                    link_term: e.target.value,
                  })
                }
              />
              <Input
                type="number"
                placeholder="Distance de lien"
                onChange={(e) =>
                  setFilterState({
                    ...filterState,
                    link_distance: isNaN(e.target.valueAsNumber)
                      ? undefined
                      : e.target.valueAsNumber,
                  })
                }
                value={link_distance}
              />
            </div>
          </div>
          <Button
            className="w-full"
            onClick={() =>
              navigate({
                route: "/",
                searchParams: {
                  ...params,
                  ...filterState,
                },
              })
            }
          >
            {isLoading ? "Application des filtres..." : "Appliquer"}
          </Button>
          <Button
            className="w-full flex gap-3"
            variant="outline"
            onClick={() =>
              navigate({
                route: "/",
                searchParams: {
                  terms: params?.terms,
                },
              })
            }
          >
            <X className="text-gray-500" />
            Effacer les filtres
          </Button>
        </div>
      </PopoverContent>
    </Popover>
  );
}

type ActiveFilter = {
  id: keyof SearchParams;
  label: string;
};

export function ActiveFilters() {
  const { data: params } = useSearchParams(Route.searchParams);

  const activeFilters = React.useMemo<ActiveFilter[]>(() => {
    if (!params) {
      return [];
    }

    const filters: ActiveFilter[] = [];

    if (params.year) {
      filters.push({ id: "year", label: `Début : ${params.year}` });
    }

    if (params.end_year) {
      filters.push({ id: "end_year", label: `Fin : ${params.end_year}` });
    }

    if (params.source && params.source !== "all") {
      const sourceLabel =
        params.source === "book"
          ? "Livre"
          : params.source === "periodical"
            ? "Périodique"
            : "Tous";
      filters.push({ id: "source", label: `Source : ${sourceLabel}` });
    }

    if (params.sort) {
      const sortLabel = params.sort === "date" ? "Date" : "Pertinence";
      filters.push({ id: "sort", label: `Tri : ${sortLabel}` });
    }

    if (params.link_term) {
      filters.push({ id: "link_term", label: `Terme associé : ${params.link_term}` });
    }

    if (params.link_distance !== undefined) {
      filters.push({ id: "link_distance", label: `Distance : ${params.link_distance}` });
    }

    return filters;
  }, [params]);

  if (activeFilters.length === 0) {
    return null;
  }

  return (
    <div className="w-full flex flex-wrap gap-2 px-2 justify-start">
      {activeFilters.map((filter) => (
        <span
          key={`${filter.id}-${filter.label}`}
          className="inline-flex items-center gap-2 rounded-full bg-primary/10 px-4 py-1 text-sm text-primary"
        >
          {filter.label}
        </span>
      ))}
    </div>
  );
}
