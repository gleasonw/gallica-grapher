import React, { useEffect } from "react";
import { GraphTicket } from "./GraphTicket";
import { ProgressType } from "../models/dbStructs";
import { apiURL } from "./apiURL";
import { useQueries } from "@tanstack/react-query";

export const SearchProgress: React.FC<{
  batchTicket: GraphTicket[];
  onFetchComplete: () => void;
  onNoRecordsFound: () => void;
}> = (props) => {
  async function fetchProgress(id: number) {
    const response = await fetch(`${apiURL}/poll/progress/${id}`);
    const data = (await response.json()) as ProgressType;
    return data;
  }
  const data = useQueries({
    queries: props.batchTicket.map((ticket) => ({
      queryKey: ["progress", ticket.id],
      queryFn: () => fetchProgress(ticket.id),
      refetchInterval: (data) => {
        if (data && data.state === "completed") {
          return false;
        } else {
          return 1000;
        }
      },
    })),
  });

  const { onFetchComplete, onNoRecordsFound } = props;
  useEffect(() => {
    if (data.every((d) => d.data?.state === "completed")) {
      onFetchComplete();
    }
  }, [data, onFetchComplete, onNoRecordsFound]);

  return <></>;
};
