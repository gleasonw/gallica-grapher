import React, { useState } from "react";
import { Paper } from "../server/routers/_app";
import { trpc } from "../utils/trpc";
import { TextInput } from "./TextInput";

export const PaperDropdown: React.FC<{
  onClick: (paper: Paper) => void;
}> = ({ onClick }) => {
  const [periodical, setPeriodical] = useState<string | undefined>();
  const papersSimilarTo = trpc.papersSimilarTo.useQuery(
    {
      title: periodical || "",
    },
    { keepPreviousData: true }
  );
  return (
    <div>
      <input
        placeholder={"search for a periodical"}
        value={periodical}
        className={"border bg-white p-5 relative max-w-full"}
        onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
          setPeriodical(e.target.value)
        }
      />
      <div className={"bg-white absolute max-w-full z-40"}>
        <ul>
          {papersSimilarTo?.data?.map((paper: Paper) => (
            <li
              key={paper.title}
              className="max-w-full border p-5 whitespace-wrap hover:bg-zinc-800 hover:text-white flex-1 hover:cursor-pointer"
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
