import React, { createContext } from "react";
import { graphStateReducer, GraphPageState } from "./GraphStateReducer";

export const GraphPageStateContext = createContext<GraphPageState | undefined>(
  undefined
);
export const GraphPageDispatchContext = createContext<
  React.Dispatch<React.ReducerAction<typeof graphStateReducer>> | undefined
>(undefined);
