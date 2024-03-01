export let apiURL: string;
if (process.env.NODE_ENV === "development") {
  apiURL = "http://localhost:8000";
} else {
  apiURL = "https://gallica-getter-little-snow-3158.fly.dev";
}
