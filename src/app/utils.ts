import { paths } from "@/types";
import createClient from "openapi-fetch";

export const client = createClient<paths>({
  baseUrl:
    process.env.NODE_ENV === "development"
      ? "http://localhost:8000"
      : "https://gallica-proxy-production.up.railway.app",
});
