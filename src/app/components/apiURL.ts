export let apiURL: string;
if (process.env.NODE_ENV === "development") {
  apiURL = "http://localhost:8000";
} else {
  apiURL = "https://gallica-proxy-production.up.railway.app";
}
