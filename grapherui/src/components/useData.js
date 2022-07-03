import {useEffect, useState} from "react";

export default function useData(url) {
  const [result, setResult] = useState(null);
  useEffect(() => {
    let ignore = false;
    fetch(url)
      .then(response => response.json())
      .then(json => {
        if (!ignore) {
          setResult(json.series);
        }
      });
    return () => {
      ignore = true;
    };
  }, [url]);
  return result;
}