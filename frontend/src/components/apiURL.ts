export let apiURL: string;
if (process.env.NODE_ENV === "development") {
  apiURL = "https://gallica-web.ew.r.appspot.com";
} else {
  apiURL = "https://gallica-web.ew.r.appspot.com";
}
