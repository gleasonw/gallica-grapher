import React, { createContext } from "react";
import { graphStateReducer } from "./GraphStateReducer";
import { GraphPageState } from "../pages/GraphPageState";

export const GraphPageStateContext = createContext<GraphPageState | undefined>(
  undefined
);
export const GraphPageDispatchContext = createContext<
  React.Dispatch<React.ReducerAction<typeof graphStateReducer>> | undefined
>(undefined);
