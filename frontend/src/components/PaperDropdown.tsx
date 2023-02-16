import React, { useState, useContext } from "react";
import { LangContext } from "../pages";
import { apiURL } from "./apiURL";
import { useQuery } from "@tanstack/react-query";
import { Paper } from "../models/dbStructs";

export const PaperDropdown: React.FC<{
  onClick: (paper: Paper) => void;
}> = ({ onClick }) => {
  async function fetchPapers(title: string) {
    if (!title) {
      return [];
    }
    const response = await fetch(`${apiURL}/api/papers/${title}`);
    const data = (await response.json()) as { papers: Paper[] };
    return data.papers;
  }
  const [periodical, setPeriodical] = useState<string | undefined>();
  const papersSimilarTo = useQuery({
    queryKey: ["papers", periodical],
    queryFn: () => fetchPapers(periodical || ""),
    staleTime: Infinity,
    keepPreviousData: true,
  });
  const { lang } = useContext(LangContext);
  return (
    <div>
      <input
        placeholder={lang === "fr" ? "rechercher un périodique" : "search for a paper"}
        value={periodical}
        className={"relative max-w-full border bg-white p-5"}
        onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
          setPeriodical(e.target.value)
        }
      />
      <div className={"absolute z-40 max-w-full bg-white"}>
        <ul>
          {papersSimilarTo?.data?.map((paper: Paper) => (
            <li
              key={paper.title}
              className="whitespace-wrap max-w-full flex-1 border p-5 hover:cursor-pointer hover:bg-zinc-800 hover:text-white"
              onClick={() => {
                setPeriodical("");
                onClick(paper);
              }}
            >
              {paper.title}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};
