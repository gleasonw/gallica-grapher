"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
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
import { Slider } from "@/components/ui/slider";
import { Filter } from "lucide-react";

export function Filters() {
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
            <Label htmlFor="startYear">Start Year:</Label>
            <Input
              id="startYear"
              type="number"
              min={1785}
              max={1945}
              className="w-20"
            />
            <Label htmlFor="endYear">End Year:</Label>
            <Input
              id="endYear"
              type="number"
              min={1785}
              max={1945}
              className="w-20"
            />
          </div>
          <Select>
            <SelectTrigger>
              <SelectValue placeholder="Source" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All</SelectItem>
              <SelectItem value="book">Book</SelectItem>
              <SelectItem value="periodical">Periodical</SelectItem>
            </SelectContent>
          </Select>
          <Select>
            <SelectTrigger>
              <SelectValue placeholder="Sort" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="relevance">Relevance</SelectItem>
              <SelectItem value="date">Date</SelectItem>
            </SelectContent>
          </Select>
          <div className="space-y-2">
            <Label>Advanced Filters</Label>
            <Input placeholder="Codes (comma-separated)" />
            <Input type="number" placeholder="Limit" />
            <Input placeholder="Link Term" />
            <Input type="number" placeholder="Link Distance" />
            <Label>OCR Quality</Label>
            <Slider defaultValue={[0.5]} max={1} step={0.1} />
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
}
