import React, { useState } from "react";
import { RevealButton } from "./RevealButton";
import { PaperDropdown } from "./PaperDropdown";
import { Paper } from "../models/dbStructs";
import { apiURL } from "./apiURL";
import { useQuery } from "@tanstack/react-query";

export const PaperSelector: React.FC<{
  papers: Paper[];
  from?: number;
  to?: number;
  onPaperAdd: (paper: Paper) => void;
  onPaperClick: (paper: Paper) => void;
  smallText?: boolean;
}> = ({ papers, from, to, onPaperAdd, onPaperClick }) => {
  async function fetchNumPapers(from?: number, to?: number) {
    const lowYear = from ? from : 0;
    const highYear = to ? to : 9999;
    const response = await fetch(
      `${apiURL}/api/numPapersOverRange/${lowYear}/${highYear}`
    );
    const data = await response.json();
    return data as number;
  }

  const [displayed, setDisplayed] = useState(false);

  const numPapers = useQuery({
    queryKey: ["numPapers", from, to],
    queryFn: () => fetchNumPapers(from, to),
    staleTime: Infinity,
  });

  return (
    <div>
      <RevealButton
        label={
          papers && papers.length > 0
            ? `In ${papers.length} ${
                papers.length === 1 ? "periodical" : "periodicals"
              }`
            : `In ${numPapers?.data || "..."} periodicals`
        }
        onClick={() => setDisplayed(!displayed)}
      />
      {displayed && (
        <>
          <div className="mt-5 flex flex-wrap gap-10">
            {papers.map((paper) => (
              <button
                className={"p-5"}
                key={paper.title}
                onClick={() => onPaperClick(paper)}
              >
                {paper.title}
              </button>
            ))}
          </div>
          <PaperDropdown onClick={onPaperAdd} />
        </>
      )}
    </div>
  );
};
