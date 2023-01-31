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
  const { data } = useQuery({
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

  const progress = data;

  if (!progress) {
    return <div>loading...</div>;
  }

  const percentProgress = Math.round(
    (progress.num_requests_sent / progress.num_requests_to_send) * 100
  );

  return (
    <div className="m-10 mb-20 flex flex-col justify-center">
      <div>
        <div>{props.ticket.terms.join(", ")}</div>
        <div>{props.ticket.papers?.map((paper) => paper.title + ", ")}</div>
        <div>
          {progress && (
            <div className={"flex flex-col gap-10"}>
              <div className="h-2.5 w-full rounded-full bg-gray-200">
                <div
                  className="h-2.5 rounded-full bg-blue-600"
                  style={{ width: `${percentProgress}%` }}
                ></div>
              </div>
              {progress.estimate_seconds_to_completion > 0 && (
                <div>{progress.estimate_seconds_to_completion}</div>
              )}
              {progress.backend_source === "gallica" && (
                <div>
                  {progress.num_results_discovered} results in the French
                  archive
                </div>
              )}
            </div>
          )}
        </div>
      </div>{" "}
    </div>
  );
};
