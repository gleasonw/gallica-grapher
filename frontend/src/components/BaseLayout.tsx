import React, { ReactNode } from "react";
import Link from "next/link";

export const BaseLayout: React.FC<{ children: ReactNode }> = ({ children }) => {
  return (
    <div className="h-screen w-screen flex flex-col">
      <div className={"flex flex-row justify-between m-5"}>
        <Link href="/" className={"text-3xl self-start"}>
          📊
        </Link>
        <div className={"flex flex-row gap-5 align-center justify-center"}>
          <Link href="/info">
            <img src={"/info.svg"} className="w-10 h-10" />
          </Link>
          <Link
            href={"https://github.com/gleasonw/gallica-grapher"}
            target={"_blank"}
          >
            <img src={"/github.svg"} className="w-10 h-10" />
          </Link>
          <Link
            target={"_blank"}
            href="https://github.com/gleasonw/gallica-grapher/issues"
            className={"text-center self-center w-10"}
          >
            Report bug
          </Link>
        </div>
      </div>
      <div className="text-3xl m-20 text-center">
        {" "}
        View word occurrences in archived French periodicals.
      </div>
      {children}
    </div>
  );
};
