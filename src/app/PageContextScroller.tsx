"use client";

import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { useState } from "react";
import * as R from "remeda";

export function PageContextScroller({
  pages,
  startChunk,
  sectionChunkSize,
}: {
  pages: React.ReactNode[];
  startChunk: number;
  sectionChunkSize: number;
}) {
  const sections = R.chunk(pages, sectionChunkSize);
  const [currentSection, setCurrentSection] = useState(startChunk);
  const showSections = sections.at(currentSection);
  if (!showSections) {
    return <div>error chunking context</div>;
  }
  return (
    <div>
      <div className="flex flex-col gap-3 h-80 overflow-auto">
        {...showSections as React.ReactNode[]}
      </div>
      <div className="flex gap-2 items-center">
        <Button
          disabled={currentSection === 0}
          variant="outline"
          onClick={() =>
            setCurrentSection(
              currentSection > 0 ? currentSection - 1 : currentSection
            )
          }
        >
          <ChevronLeft />
        </Button>
        <Button
          disabled={currentSection === sections.length - 1}
          variant="outline"
          onClick={() =>
            setCurrentSection(
              currentSection < sections.length - 1
                ? currentSection + 1
                : currentSection
            )
          }
        >
          <ChevronRight />
        </Button>
      </div>
    </div>
  );
}
