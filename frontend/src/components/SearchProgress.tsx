import React, { useEffect } from "react";
import { GraphTicket } from "./GraphTicket";
import { ProgressType } from "../models/dbStructs";
import { apiURL } from "./apiURL";
import { useQuery } from "@tanstack/react-query";

export const SearchProgress: React.FC<{
  ticket: GraphTicket;
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

  return <></>;
};
