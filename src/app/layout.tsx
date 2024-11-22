import { Providers } from "@/src/app/providers";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <script
          defer
          data-domain="gallicagrapher.com"
          src="https://plausible.io/js/script.js"
        ></script>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
