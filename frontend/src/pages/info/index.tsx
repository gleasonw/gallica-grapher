import Explain from "./explain.mdx";
import { BaseLayout } from "../../components/BaseLayout";

export default function Info() {
  return (
    <BaseLayout>
      <article className="text-justify m-auto prose prose-lg p-2 lg:prose-lg xl:prose-2xl">
        <Explain />
      </article>
    </BaseLayout>
  );
}
