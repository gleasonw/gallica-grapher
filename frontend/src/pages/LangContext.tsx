import React, { createContext } from "react";

export const LangContext = createContext<{
  lang: "fr" | "en";
  setLang: React.Dispatch<React.SetStateAction<"fr" | "en">>;
}>({ lang: "fr", setLang: () => {} });
