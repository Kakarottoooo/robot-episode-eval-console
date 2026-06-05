import { EpisodeTable } from "@/components/EpisodeTable";
import { getEpisodes } from "@/lib/api";

type SearchParams = Promise<{
  success?: string;
  environment?: string;
  policy_name?: string;
  failure_reason?: string;
}>;

export default async function EpisodesPage({
  searchParams,
}: {
  searchParams: SearchParams;
}) {
  const params = await searchParams;
  const episodes = await getEpisodes({
    success: params.success === undefined ? undefined : params.success === "true",
    environment: params.environment || undefined,
    policy_name: params.policy_name || undefined,
    failure_reason: params.failure_reason || undefined,
    limit: 300,
  });

  return (
    <div className="space-y-5">
      <div className="panel px-5 py-4">
        <form className="grid gap-3 md:grid-cols-5">
          <select name="success" defaultValue={params.success ?? ""} className="rounded-md border border-line bg-white px-3 py-2 text-sm">
            <option value="">All outcomes</option>
            <option value="true">Success only</option>
            <option value="false">Failed only</option>
          </select>
          <select name="environment" defaultValue={params.environment ?? ""} className="rounded-md border border-line bg-white px-3 py-2 text-sm">
            <option value="">All environments</option>
            <option value="simulation">Simulation</option>
            <option value="real_robot">Real robot</option>
          </select>
          <input name="policy_name" defaultValue={params.policy_name ?? ""} placeholder="policy name" suppressHydrationWarning className="rounded-md border border-line bg-white px-3 py-2 text-sm" />
          <input name="failure_reason" defaultValue={params.failure_reason ?? ""} placeholder="failure reason" suppressHydrationWarning className="rounded-md border border-line bg-white px-3 py-2 text-sm" />
          <button className="rounded-md bg-graphite px-3 py-2 text-sm font-medium text-white">Apply filters</button>
        </form>
      </div>
      <EpisodeTable episodes={episodes} />
    </div>
  );
}
