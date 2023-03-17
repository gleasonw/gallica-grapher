import React, { createContext } from "react";
import { searchStateReducer } from "./SearchStateReducer";
import { SearchPageState } from "../components/SearchStateReducer";

export const SearchPageStateContext = createContext<
  SearchPageState | undefined
>(undefined);
export const SearchPageDispatchContext = createContext<React.Dispatch<
  React.ReducerAction<typeof searchStateReducer>
> | null>(null);
