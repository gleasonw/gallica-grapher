import { addQueryParamsIfExist } from "../utils/addQueryParamsIfExist";
import { apiURL } from "./apiURL";
import { useQuery } from "react-query";

export function ImageSnippet({
  ark,
  term,
  pageNumber,
}: {
  ark: string;
  term: string;
  pageNumber: number;
}) {
  const { data, isLoading } = useQuery({
    queryFn: async () => {
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
    },
    queryKey: ["image", ark, term, pageNumber],
    keepPreviousData: true,
  });

  if (isLoading) {
    return <div>Chargement...</div>;
  }

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
