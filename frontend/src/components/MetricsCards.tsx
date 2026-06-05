import type { LucideIcon } from "lucide-react";

type MetricCard = {
  label: string;
  value: string | number;
  icon: LucideIcon;
};

export function MetricsCards({ cards }: { cards: MetricCard[] }) {
  return (
    <>
      {cards.map((card) => {
        const Icon = card.icon;
        return (
          <div key={card.label} className="panel p-5">
            <div className="mb-4 flex items-center justify-between">
              <span className="metric-label">{card.label}</span>
              <span className="flex h-8 w-8 items-center justify-center rounded-md bg-slate-100 text-teal">
                <Icon size={17} />
              </span>
            </div>
            <div className="metric-value">{card.value}</div>
          </div>
        );
      })}
    </>
  );
}
