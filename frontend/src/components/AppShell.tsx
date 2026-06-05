"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BarChart3, Bot, Database, FlaskConical, LayoutDashboard } from "lucide-react";

const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/episodes", label: "Episodes", icon: Database },
  { href: "/experiments", label: "Experiments", icon: FlaskConical },
  { href: "/comparison", label: "Comparison", icon: BarChart3 },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen bg-[#eef3f7]">
      <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-line bg-white lg:block">
        <div className="flex h-16 items-center gap-3 border-b border-line px-5">
          <div className="flex h-9 w-9 items-center justify-center rounded-md bg-graphite text-white">
            <Bot size={19} />
          </div>
          <div>
            <div className="text-sm font-semibold text-graphite">Robot Eval</div>
            <div className="text-xs text-slate-500">Episode console</div>
          </div>
        </div>
        <nav className="space-y-1 px-3 py-4">
          {navItems.map((item) => {
            const active = item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium ${
                  active
                    ? "bg-slate-900 text-white"
                    : "text-slate-600 hover:bg-slate-100 hover:text-graphite"
                }`}
              >
                <Icon size={17} />
                {item.label}
              </Link>
            );
          })}
        </nav>
      </aside>

      <div className="lg:pl-64">
        <header className="sticky top-0 z-10 border-b border-line bg-[#eef3f7]/95 px-4 py-3 backdrop-blur lg:px-7">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h1 className="text-lg font-semibold text-graphite">Evaluation Console</h1>
              <p className="text-sm text-slate-500">Robot episode data, evaluation jobs, and policy comparisons</p>
            </div>
            <div className="flex items-center gap-2 rounded-md border border-line bg-white px-3 py-2 text-xs font-medium text-slate-600">
              <span className="h-2 w-2 rounded-full bg-teal" />
              API http://localhost:8000
            </div>
          </div>
          <nav className="mt-3 flex gap-2 overflow-x-auto pb-1 lg:hidden">
            {navItems.map((item) => {
              const active = item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`inline-flex shrink-0 items-center gap-2 rounded-md px-3 py-2 text-sm font-medium ${
                    active
                      ? "bg-slate-900 text-white"
                      : "border border-line bg-white text-slate-600"
                  }`}
                >
                  <Icon size={16} />
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </header>
        <main className="px-4 py-5 lg:px-7">{children}</main>
      </div>
    </div>
  );
}
