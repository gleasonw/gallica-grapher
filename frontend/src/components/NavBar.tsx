import { AnimatePresence, motion } from "framer-motion";
import Link from "next/link";
import Image from "next/image";
import React from "react";
import { useRouter } from "next/router";
import { listenForOutsideClicks } from "./utils/listenForOutsideClicks";

const pages = {
  "": "Graph",
  context: "Context",
  info: "Info",
};

type urlPage = keyof typeof pages;

export default function NavBar() {
  const [showSidebar, setShowSidebar] = React.useState(false);
  const menuRef = React.useRef<HTMLElement | null>(null);
  const [listening, setListening] = React.useState(false);
  const [lang, setLang] = React.useState<"fr" | "en">("fr");
  const router = useRouter();
  const currentPage = router.pathname.split("/")[1] as urlPage;
  const linkStyle = "p-5 hover:cursor-pointer";
  let homeLinkStyle = linkStyle;
  let exploreLinkStyle = linkStyle;
  let infoLinkStyle = linkStyle;
  const borderBottomFocus = " border-b border-blue-500 border-b-4";
  if (currentPage === "") {
    homeLinkStyle += borderBottomFocus;
  } else if (currentPage === "context") {
    exploreLinkStyle += borderBottomFocus;
  } else if (currentPage === "info") {
    infoLinkStyle += borderBottomFocus;
  }

  React.useEffect(() => {
    listenForOutsideClicks(listening, setListening, menuRef, setShowSidebar);
  }, [listening, menuRef, setShowSidebar]);

  const styleMap = {
    "": homeLinkStyle,
    context: exploreLinkStyle,
    info: infoLinkStyle,
  };

  return (
    <div className="flex flex-col">
      <div className="flex flex-col sticky top-0 z-50">
        <div
          className={
            "flex flex-row items-center justify-between p-5 border-b-2 bg-white shadow-sm"
          }
        >
          <div className={"flex"}>
            <svg
              focusable="false"
              viewBox="0 0 24 24"
              className="w-10 hover:cursor-pointer hover:bg-zinc-100 rounded-full"
              onClick={() => setShowSidebar(!showSidebar)}
            >
              <path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"></path>
            </svg>
            <Link className={"p-5 text-3xl"} href={"/"}>
              Gallica Grapher
            </Link>
            <div className="hidden lg:flex xl:flex items-center">
              {Object.keys(pages).map((link) => (
                <Link
                  key={link}
                  className={styleMap[link as keyof typeof pages]}
                  href={`/${link}`}
                >
                  {pages[link as keyof typeof pages]}
                </Link>
              ))}
            </div>
          </div>
          <div className={"flex flex-row gap-5 align-center justify-center"}>
            <Link
              href={"https://github.com/gleasonw/gallica-grapher"}
              target={"_blank"}
            >
              <Image
                src={"/github.svg"}
                width={40}
                height={40}
                alt={"Github"}
              />
            </Link>
          </div>
        </div>
        <AnimatePresence>
          {showSidebar && (
            <motion.div
              initial={{ x: -1000 }}
              animate={{ x: 0 }}
              exit={{ x: -1000 }}
              transition={{ duration: 0.2 }}
              className={"sticky top-0"}
            >
              <div
                className={
                  "absolute bg-white z-40 flex flex-col gap-1 p-2 h-screen border-r shadow-md"
                }
              >
                {Object.keys(pages).map((link) => (
                  <Link
                    key={link}
                    className={
                      "p-5 w-60 hover:bg-blue-100 rounded-lg hover:cursor-pointer"
                    }
                    href={`/${link}`}
                  >
                    {pages[link as keyof typeof pages]}
                  </Link>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
