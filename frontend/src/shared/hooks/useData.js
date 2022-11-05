import {useEffect, useState} from "react";

export default function useData(url) {
  const [result, setResult] = useState(null);
  useEffect(() => {
    let ignore = false;
    fetch(url, {mode: 'cors'})
      .then(response => response.json())
      .then(json => {
        if (!ignore) {
          setResult(json);
        }
      });
    return () => {
      ignore = true;
    };
  }, [url]);
  return result;
}

//Credits Dan Abramov