import { InferGetStaticPropsType } from "next";
import { getStaticProps } from "../pages";
import { createContext } from "react";

export const StaticPropContext = createContext<
  InferGetStaticPropsType<typeof getStaticProps> | undefined
>(undefined);
