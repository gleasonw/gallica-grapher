"use client";

import { PageProps } from "@/.next/types/app/page";
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
import { Route } from "@/src/app/routeType";
import { Calendar, Filter, Link } from "lucide-react";
import { useSearchParams } from "next-typesafe-url/app";
import React from "react";

export function Filters() {
  const { data: params } = useSearchParams(Route.searchParams);
  const [filterState, setFilterState] = React.useState<
    PageProps["searchParams"] | undefined
  >(params);
  const { year, end_year, source, sort, link_term, link_distance } =
    filterState ?? {};

  const { isLoading, navigate } = useNavigateWithLoading();
  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="outline" size="lg" className="shadow-lg">
          <Filter className="h-4 w-4 mr-2" />
          Filters
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
              value={end_year}
              onChange={(e) =>
                setFilterState({
                  ...filterState,
                  end_year: e.target.valueAsNumber,
                })
              }
              placeholder="Start year"
            />
            <Input
              id="endYear"
              type="number"
              min={1785}
              max={1945}
              value={year}
              onChange={(e) =>
                setFilterState({
                  ...filterState,
                  year: e.target.valueAsNumber,
                })
              }
              placeholder="End year"
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
              <SelectItem value="all">All</SelectItem>
              <SelectItem value="book">Book</SelectItem>
              <SelectItem value="periodical">Periodical</SelectItem>
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
              <SelectValue placeholder="Sort" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="relevance">Relevance</SelectItem>
              <SelectItem value="date">Date</SelectItem>
            </SelectContent>
          </Select>
          <div className="flex w-full justify-between items-center">
            <Link />
            <div className="flex gap-2 flex-col">
              <Input
                placeholder="Link Term"
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
                placeholder="Link Distance"
                onChange={(e) =>
                  setFilterState({
                    ...filterState,
                    link_distance: e.target.valueAsNumber,
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
            {isLoading ? "Applying filters..." : "Apply"}
          </Button>
        </div>
      </PopoverContent>
    </Popover>
  );
}
