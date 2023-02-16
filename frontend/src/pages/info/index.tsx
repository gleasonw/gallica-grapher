import Explain from "./explain.mdx";
import { BaseLayout } from "../../components/BaseLayout";
import { useRouter } from "next/router";

export default function Info() {
  const router = useRouter();
  const { queryLang } = router.query;
  return (
    <BaseLayout>
      <article className="text-justify m-auto prose prose-lg p-2 lg:prose-lg xl:prose-2xl">
        <Explain />
      </article>
    </BaseLayout>
  );
}
