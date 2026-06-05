import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { EpisodeViewer } from "@/components/EpisodeViewer";
import { getEpisode, getEpisodeSeries } from "@/lib/api";

type Params = Promise<{ episodeId: string }>;

export default async function EpisodeDetailPage({ params }: { params: Params }) {
  const { episodeId } = await params;
  const [episode, series] = await Promise.all([
    getEpisode(episodeId),
    getEpisodeSeries(episodeId),
  ]);
  if (!episode) {
    notFound();
  }

  return (
    <div className="space-y-4">
      <Link href="/episodes" className="inline-flex items-center gap-2 text-sm font-medium text-slate-600 hover:text-graphite">
        <ArrowLeft size={16} />
        Episodes
      </Link>
      <EpisodeViewer episode={episode} series={series} />
    </div>
  );
}
