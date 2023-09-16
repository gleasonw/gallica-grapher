export function addQueryParamsIfExist(
  url: string,
  params: Record<string, any>
) {
  const urlParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (
      value !== undefined &&
      value !== null &&
      value !== "" &&
      !Array.isArray(value)
    ) {
      urlParams.append(key, value);
    } else if (Array.isArray(value)) {
      value.forEach((v) => {
        if (typeof v === "string" && v.length > 0) {
          urlParams.append(key, v);
        }
      });
    }
  });
  return `${url}?${urlParams.toString()}`;
}
