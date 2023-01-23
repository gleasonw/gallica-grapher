import React, { useEffect } from "react";
import { trpc } from "../utils/trpc";
import { Ticket } from "../pages/index";

export const SearchProgress: React.FC<{
  ticket: Ticket;
  onFetchComplete: (backend_source: "gallica" | "pyllica") => void;
}> = (props) => {
  const { data } = trpc.progress.useQuery(
    {
      id: props.ticket.id,
    },
    {
      refetchInterval: (data) => {
        if (data && data.state === "completed") {
          return false;
        } else {
          return 1000;
        }
      },
    }
  );

  const { onFetchComplete } = props;
  useEffect(() => {
    if (data && data.state === "completed") {
      onFetchComplete(data.backend_source);
    }
  }, [data, onFetchComplete]);

  const progress = data;

  if (!progress) {
    return <div>loading...</div>;
  }

  const percentProgress = Math.round(
    (progress.num_requests_sent / progress.num_requests_to_send) * 100
  );

  return (
    <div className="flex flex-col justify-center m-10 mb-20">
      <div>
        <div>{props.ticket.terms.join(", ")}</div>
        <div>{props.ticket.papers?.map((paper) => paper.title + ", ")}</div>
        <div>
          {progress && (
            <div className={"flex flex-col gap-10"}>
              <div className="w-full bg-gray-200 rounded-full h-2.5">
                <div
                  className="bg-blue-600 h-2.5 rounded-full"
                  style={{ width: `${percentProgress}%` }}
                ></div>
              </div>
              {progress.estimate_seconds_to_completion > 0 && (
                <div>{progress.estimate_seconds_to_completion}</div>
              )}
              <div>
                {progress.num_results_discovered} results in the French archive
              </div>
            </div>
          )}
        </div>
      </div>{" "}
    </div>
  );
};
