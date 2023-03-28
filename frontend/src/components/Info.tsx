import { useContext } from "react";
import { LangContext } from "./LangContext";
import EnExplain from "./assets/explain_en.mdx";
import FrExplain from "./assets/explain_fr.mdx";

export default function Info() {
  const { lang } = useContext(LangContext);
  return (
    <article className="text-justify m-auto prose prose-lg p-2 lg:prose-lg xl:prose-2xl mt-20 mb-20">
      {lang === "en" ? <EnExplain /> : <FrExplain />}
    </article>
  );
}
