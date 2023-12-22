import { addQueryParamsIfExist } from "../utils/addQueryParamsIfExist";
import Image from "next/image";
import { apiURL } from "./apiURL";

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
    const url = addQueryParamsIfExist(`${apiURL}/api/image`, {
      ark: ark,
      term: term,
      page: pageNumber,
    });
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
        <img src={data.image} alt={term} />
      ) : (
        <div>aucune image disponible 😔</div>
      )}
    </div>
  );
}
