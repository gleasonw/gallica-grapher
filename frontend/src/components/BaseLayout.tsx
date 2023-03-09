import React, { ReactNode } from "react";
import Link from "next/link";
import Image from "next/image";
import { useContext } from "react";
import { LangContext } from "../pages";

interface BaseLayoutProps {
  children: ReactNode;
  onToggleLang?: () => void;
}

export const BaseLayout: React.FC<BaseLayoutProps> = (props) => {
  const lang = useContext(LangContext);
  return (
    <div className="h-screen w-screen flex flex-col">
      <div className={"flex flex-row items-center justify-between p-5 border-b bg-slate-100"}>
        <Link href="/" className={"text-3xl self-start"}>
          📊
        </Link>
        <div className={"flex flex-row gap-5 align-center justify-center"}>
          <label className={"relative inline-flex items-center cursor-pointer"}>
            <span className={"mr-3"}>fr</span>
            <input
              onChange={props.onToggleLang}
              type="checkbox"
              value=""
              className={"sr-only peer"}
            />
            <div
              className={
                "relative w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all"
              }
            ></div>
            <span className={"ml-3"}>en</span>
          </label>

          <Link href="/info">
            <Image src={"/info.svg"} width={40} height={40} alt={"Info page"} />
          </Link>
          <Link
            href={"https://github.com/gleasonw/gallica-grapher"}
            target={"_blank"}
          >
            <Image src={"/github.svg"} width={40} height={40} alt={"Github"} />
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
      {props.children}
    </div>
  );
};
