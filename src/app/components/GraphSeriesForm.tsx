"use client";

import React from "react";
import InputBubble from "./InputBubble";
import { useSearchState } from "../composables/useSearchState";
import { useSubmit } from "./LoadingProvider";
import { Spinner } from "./Spinner";
import { Button } from "./design_system/button";

export function GraphSeriesForm({ children }: { children?: React.ReactNode }) {
  const { terms } = useSearchState();
  const [localTerm, setLocalTerm] = React.useState<string>("");

  const { handleSubmit, isPending } = useSubmit();

  function submitForm(args?: unknown) {
    if (typeof args === "object") {
      handleSubmit({
        ...args,
        terms: terms ? [...terms, localTerm] : [localTerm],
      });
    } else {
      handleSubmit({
        terms: terms ? [...terms, localTerm] : [localTerm],
      });
    }
  }

  return (
    <>
      <form
        className={
          "w-full flex flex-col justify-center items-center rounded-full gap-5"
        }
        onSubmit={(e) => {
          e.preventDefault();
          submitForm();
        }}
      >
        <InputBubble
          word={localTerm}
          onWordChange={(word) => setLocalTerm(word)}
        >
          <Button className="absolute top-4 right-5 rounded-full w-24">
            {isPending ? <Spinner isFetching /> : "Explore"}
          </Button>
        </InputBubble>
      </form>
      {children}
    </>
  );
}
