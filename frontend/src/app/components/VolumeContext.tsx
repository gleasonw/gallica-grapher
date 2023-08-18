import { fetchVolumeContext } from "./fetchContext";
import ContextViewer from "./ContextViewer";
import { ImageSnippet } from "./ImageSnippet";

export async function VolumeContext({
  ark,
  term,
  pageNum,
  showImage,
}: {
  ark: string;
  term: string;
  pageNum?: number;
  showImage?: boolean;
}) {
  const volumeData = await fetchVolumeContext({ ark, term });
  return (
    <ContextViewer data={volumeData} ark={ark}>
      {showImage && (
        <ImageSnippet
          ark={ark}
          term={term}
          pageNumber={pageNum ?? volumeData[0].page_num}
        />
      )}
    </ContextViewer>
  );
}
