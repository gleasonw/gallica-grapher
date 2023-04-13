export let apiURL: string;
if (process.env.NODE_ENV === "development") {
  apiURL = "http://127.0.0.1:8000";
} else {
  apiURL = "https://gallica-web.ew.r.appspot.com";
}
