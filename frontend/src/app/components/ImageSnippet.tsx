import { addQueryParamsIfExist } from "../utils/addQueryParamsIfExist";
import Image from "next/image";
import * as Dialog from "@radix-ui/react-dialog";

export async function ImageSnippet({
  ark,
  term,
  pageNumber,
}: {
  ark: string;
  term: string;
  pageNumber: number;
}) {
  async function doFetch() {
    const url = addQueryParamsIfExist(
      `https://gallica-grapher-production.up.railway.app/api/image`,
      {
        ark: ark,
        term: term,
        page: pageNumber,
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
        <Image src={data.image} alt={term} width={900} height={100} />
      ) : (
        <div>aucune image disponible 😔</div>
      )}
    </div>
  );
}
