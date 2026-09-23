import React from "react";
import { NavLink } from "react-router-dom";

const NAV_ITEMS = [
  { to: "/", label: "Dashboard", icon: "grid" },
  { to: "/assets", label: "Assets", icon: "server" },
  { to: "/risks", label: "Risks", icon: "alert" },
  { to: "/advisor", label: "AI Advisor", icon: "bulb" },
  { to: "/simulation", label: "What-if Simulation", icon: "flask" },
  { to: "/optimization", label: "Investment Optimization", icon: "target" },
];

function Icon({ name, className }: { name: string; className?: string }) {
  const common = { className, fill: "none", stroke: "currentColor", strokeWidth: 1.8, viewBox: "0 0 24 24" };
  switch (name) {
    case "grid":
      return (
        <svg {...common}><rect x="3" y="3" width="7" height="7" rx="1.5" /><rect x="14" y="3" width="7" height="7" rx="1.5" /><rect x="3" y="14" width="7" height="7" rx="1.5" /><rect x="14" y="14" width="7" height="7" rx="1.5" /></svg>
      );
    case "server":
      return (
        <svg {...common}><rect x="3" y="4" width="18" height="6" rx="1.5" /><rect x="3" y="14" width="18" height="6" rx="1.5" /><circle cx="7" cy="7" r="0.6" fill="currentColor" /><circle cx="7" cy="17" r="0.6" fill="currentColor" /></svg>
      );
    case "alert":
      return (
        <svg {...common}><path d="M12 3 2 20h20L12 3Z" /><path d="M12 10v4" /><circle cx="12" cy="17" r="0.6" fill="currentColor" /></svg>
      );
    case "bulb":
      return (
        <svg {...common}><path d="M9 18h6" /><path d="M10 21h4" /><path d="M12 3a6 6 0 0 0-3.6 10.8c.5.4.8 1 .8 1.7V16h5.6v-.5c0-.7.3-1.3.8-1.7A6 6 0 0 0 12 3Z" /></svg>
      );
    case "flask":
      return (
        <svg {...common}><path d="M9 3h6" /><path d="M10 3v6l-5.5 9.5A2 2 0 0 0 6.2 21h11.6a2 2 0 0 0 1.7-2.5L14 9V3" /></svg>
      );
    case "target":
      return (
        <svg {...common}><circle cx="12" cy="12" r="8" /><circle cx="12" cy="12" r="4" /><circle cx="12" cy="12" r="0.6" fill="currentColor" /></svg>
      );
    case "shield":
      return (
        <svg {...common}><path d="M12 3 4 6v6c0 5 3.4 8.4 8 9 4.6-.6 8-4 8-9V6l-8-3Z" /><path d="m9 12 2 2 4-4" /></svg>
      );
    case "doc":
      return (
        <svg {...common}><path d="M7 3h7l4 4v14H7Z" /><path d="M14 3v4h4" /><path d="M9 13h6" /><path d="M9 17h6" /></svg>
      );
    default:
      return null;
  }
}

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen bg-base-950">
      <aside className="fixed inset-y-0 left-0 z-20 w-64 border-r border-base-600 bg-base-900">
        <div className="flex h-16 items-center gap-2.5 border-b border-base-600 px-5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-500/15 text-brand-400">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
              <path d="M12 3 4 6v6c0 5 3.4 8.4 8 9 4.6-.6 8-4 8-9V6l-8-3Z" />
              <path d="m9 12 2 2 4-4" />
            </svg>
          </div>
          <div>
            <p className="text-sm font-semibold leading-tight text-ink-100">CyberRisk IQ</p>
            <p className="text-[11px] leading-tight text-ink-500">SIH26105 Prototype</p>
          </div>
        </div>
        <nav className="flex flex-col gap-1 p-3">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition ${
                  isActive
                    ? "bg-brand-500/12 text-brand-400"
                    : "text-ink-300 hover:bg-base-700 hover:text-ink-100"
                }`
              }
            >
              <Icon name={item.icon} className="h-[18px] w-[18px] shrink-0" />
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="absolute bottom-0 left-0 right-0 border-t border-base-600 p-4">
          <p className="text-[11px] leading-relaxed text-ink-500">
            Prototype methodology only. Figures are illustrative, derived from a seeded demo dataset.
          </p>
        </div>
      </aside>

      <div className="flex flex-1 flex-col pl-64">
        <header className="sticky top-0 z-10 flex h-16 items-center justify-between border-b border-base-600 bg-base-950/90 px-6 backdrop-blur">
          <div>
            <p className="text-xs text-ink-500">Organization</p>
            <p className="text-sm font-medium text-ink-100">Demo Financial Services Ltd.</p>
          </div>
          <div className="flex items-center gap-3">
            <span className="rounded-full border border-base-600 bg-base-800 px-3 py-1 text-xs text-ink-300">
              Continuous Monitoring: Active
            </span>
            <div className="flex items-center gap-2 rounded-full border border-base-600 bg-base-800 py-1 pl-1 pr-3">
              <div className="flex h-7 w-7 items-center justify-center rounded-full bg-brand-500/20 text-xs font-semibold text-brand-400">
                C
              </div>
              <span className="text-xs font-medium text-ink-100">CISO</span>
            </div>
          </div>
        </header>
        <main className="flex-1 px-6 py-6">{children}</main>
      </div>
    </div>
  );
}
