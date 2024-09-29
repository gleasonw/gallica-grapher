export let apiURL: string;
if (process.env.NODE_ENV === "development") {
  apiURL = "http://localhost:8000";
} else {
  apiURL =
    process.env.API_URL ?? "https://gallica-proxy-production.up.railway.app";
}
