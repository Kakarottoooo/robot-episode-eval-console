import { Activity, Database, FlaskConical, Gauge } from "lucide-react";
import { FailureDistribution } from "@/components/FailureDistribution";
import { JobsTable } from "@/components/JobsTable";
import { MetricsCards } from "@/components/MetricsCards";
import { PolicyComparisonChart } from "@/components/PolicyComparisonChart";
import { RecentEpisodes } from "@/components/RecentEpisodes";
import { getEpisodes, getEvalJobs, getExperiments } from "@/lib/api";
import { buildDashboardMetrics, buildFailureDistribution, buildPolicyRows } from "@/lib/metrics";

export default async function DashboardPage() {
  const [episodes, experiments, jobs] = await Promise.all([
    getEpisodes({ limit: 200 }),
    getExperiments(),
    getEvalJobs(),
  ]);
  const metrics = buildDashboardMetrics(episodes, experiments);
  const failures = buildFailureDistribution(episodes);
  const policyRows = buildPolicyRows(experiments, episodes);

  return (
    <div className="space-y-5">
      <div className="grid gap-4 md:grid-cols-4">
        <MetricsCards
          cards={[
            { label: "Total episodes", value: metrics.totalEpisodes, icon: Database },
            { label: "Experiments", value: metrics.totalExperiments, icon: FlaskConical },
            { label: "Success rate", value: `${metrics.successRate}%`, icon: Gauge },
            { label: "Avg duration", value: `${metrics.avgDuration}s`, icon: Activity },
          ]}
        />
      </div>

      <div className="grid gap-5 xl:grid-cols-[1.1fr_0.9fr]">
        <PolicyComparisonChart rows={policyRows.slice(0, 6)} />
        <FailureDistribution rows={failures} />
      </div>

      <div className="grid gap-5 xl:grid-cols-[1fr_0.9fr]">
        <RecentEpisodes episodes={episodes.slice(0, 8)} />
        <JobsTable jobs={jobs.slice(0, 8)} />
      </div>
    </div>
  );
}
