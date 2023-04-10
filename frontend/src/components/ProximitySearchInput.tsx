import React from "react";
import { LangContext } from "./LangContext";
import link from "./assets/link.svg";
import Image from "next/image";
import { strings } from "../pages/context";

export function ProximitySearchInput(props: {
  onSetLinkTerm: (linkTerm: string) => void;
  onSetLinkDistance?: (linkDistance?: number) => void;
  linkTerm?: string;
  linkDistance?: number;
}) {
  const { lang } = React.useContext(LangContext);
  const translation = strings[lang];
  return (
    <div className="flex flex-wrap gap-5">
      <input
        type="text"
        value={props.linkTerm || ""}
        onChange={(e) => props.onSetLinkTerm(e.target.value)}
        className={"border p-2 rounded-lg shadow-sm"}
        placeholder={translation.linkTerm}
      />
      <Image src={link} alt={"proximity search icon"} width={30} height={30} />
      {props.onSetLinkDistance && (
        <input
          type="number"
          value={props.linkDistance}
          onChange={(e) => {
            const numVal = parseInt(e.target.value);
            if (typeof numVal === "number" && !isNaN(numVal) && numVal >= 0) {
              props.onSetLinkDistance!(numVal);
            } else if (e.target.value === "") {
              props.onSetLinkDistance!(undefined);
            }
          }}
          className={"border p-2 rounded-lg shadow-sm"}
          placeholder={translation.linkDistance}
        />
      )}
    </div>
  );
}
