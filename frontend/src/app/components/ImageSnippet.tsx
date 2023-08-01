import { addQueryParamsIfExist } from "../utils/addQueryParamsIfExist";
import Link from "next/link";
import Image from "next/image";
import * as Dialog from "@radix-ui/react-dialog";

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
    <div className={"relative w-full h-full"}>
      {data?.image ? (
        <Image src={data.image} alt={term} fill={true} objectFit="contain" />
      ) : (
        <div>aucune image disponible 😔</div>
      )}
    </div>
  );
}
