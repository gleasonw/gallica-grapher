export let apiURL: string;
if (process.env.NODE_ENV === "development") {
  apiURL = "https://gallica-grapher-production-6518.up.railway.app/";
} else {
  apiURL = "https://gallica-grapher-production-6518.up.railway.app/";
}
