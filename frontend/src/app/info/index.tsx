import NavBar from "../../components/NavBar";
import FrExplain from "./explain_fr.mdx";

export default function Info() {
  return (
    <>
      <NavBar />
      <article className="text-justify m-auto prose prose-lg p-2 lg:prose-lg xl:prose-2xl mt-20 mb-20">
        {<FrExplain />}
      </article>
    </>
  );
}
