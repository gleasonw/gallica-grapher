import React, { useState } from "react";
import { Paper } from "../server/routers/_app";
import { trpc } from "../utils/trpc";
import { RevealButton } from "./RevealButton";
import { PaperDropdown } from "./PaperDropdown";

export const PaperSelector: React.FC<{
  papers: Paper[];
  from: number;
  to: number;
  onPaperAdd: (paper: Paper) => void;
  onPaperClick: (paper: Paper) => void;
  smallText?: boolean;
}> = ({ papers, from, to, onPaperAdd, onPaperClick }) => {
  const [displayed, setDisplayed] = useState(false);

  const numPapers = trpc.numPapers.useQuery(
    {
      from: from,
      to: to,
    },
    { staleTime: Infinity }
  );

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
          <div className="flex flex-wrap mt-5 gap-10">
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
