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
      <div
        className={
          "flex flex-row items-center justify-between p-5 border-b-2"
        }
      >
        <div className={"flex"}>
          <Link className={"p-5 text-3xl"} href="/">
            Gallica Grapher
          </Link>
          <Link href="/" className={"p-5"}>
            Graph
          </Link>
          <Link href="/explore" className={"p-5"}>
            Context
          </Link>

          <Link href="/info" className={"p-5"}>
            Info
          </Link>
        </div>
        <div className={"flex flex-row gap-5 align-center justify-center"}>
          <select
            onChange={props.onToggleLang}
            value={lang.lang}
            className={""}
          >
            <option value="fr">Français</option>
            <option value="en">English</option>
          </select>

          <Link
            href={"https://github.com/gleasonw/gallica-grapher"}
            target={"_blank"}
          >
            <Image src={"/github.svg"} width={40} height={40} alt={"Github"} />
          </Link>
        </div>
      </div>
      {props.children}
    </div>
  );
};
