import { addQueryParamsIfExist } from "../utils/addQueryParamsIfExist";
import Link from "next/link";
import Image from "next/image";

export async function ImageSnippet({
  ark,
  term,
  url,
}: {
  ark: string;
  term: string;
  url: string;
}) {
  const last_el = url.split("/").pop();
  const page_sec = last_el?.split(".")?.[0];
  const page = page_sec?.slice(1);

  async function doFetch() {
    const url = addQueryParamsIfExist(
      `https://gallica-grapher.ew.r.appspot.com/api/image`,
      {
        ark: ark,
        term: term,
        page: page,
      }
    );
    const response = await fetch(url);
    if (response.status !== 200) {
      return { image: "" };
    }
    const imgString = (await response.json()) as { image: string };
    return imgString;
  }

  const data = await doFetch();

  return (
    <Link href={url} target={"_blank"}>
      {data?.image ? (
        <Image src={data.image} alt={term} width={700} height={80} />
      ) : (
        <div>aucune image disponible 😔</div>
      )}
    </Link>
  );
}
