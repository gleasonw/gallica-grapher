import React, { useEffect } from "react";
import { Ticket } from "../pages/index";
import { ProgressType } from "../models/dbStructs";
import { apiURL } from "./apiURL";
import { useQuery } from "@tanstack/react-query";

export const SearchProgress: React.FC<{
  ticket: Ticket;
  onFetchComplete: (backend_source: "gallica" | "pyllica") => void;
  onNoRecordsFound: () => void;
}> = (props) => {
  async function fetchProgress() {
    const response = await fetch(`${apiURL}/poll/progress/${props.ticket.id}`);
    const data = (await response.json()) as ProgressType;
    return data;
  }
  const { data, isLoading } = useQuery({
    queryKey: ["progress", props.ticket.id],
    queryFn: fetchProgress,
    refetchInterval: (data) => {
      if (data && data.state === "completed") {
        return false;
      } else {
        return 1000;
      }
    },
  });

  const { onFetchComplete, onNoRecordsFound } = props;
  useEffect(() => {
    if (data && data.state === "no_records") {
      onNoRecordsFound();
    }
    if (data && data.state === "completed") {
      onFetchComplete(data.backend_source);
    }
  }, [data, onFetchComplete, onNoRecordsFound]);

  if (isLoading || data?.state !== "completed") {
    return (
      <div className="flex items-center justify-center">
        <div
          className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite]"
          role="status"
        >
          <span className="!absolute !-m-px !h-px !w-px !overflow-hidden !whitespace-nowrap !border-0 !p-0 ![clip:rect(0,0,0,0)]">
            Loading...
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className="m-10 mb-20 flex flex-col justify-center">
      <div>
        <div>{props.ticket.terms.join(", ")}</div>
      </div>{" "}
    </div>
  );
};
