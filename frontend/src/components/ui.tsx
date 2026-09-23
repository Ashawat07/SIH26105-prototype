import React from "react";
import { riskColor } from "../lib/api";

export function Card({
  children,
  className = "",
  title,
  subtitle,
  action,
}: {
  children: React.ReactNode;
  className?: string;
  title?: string;
  subtitle?: string;
  action?: React.ReactNode;
}) {
  return (
    <div className={`rounded-xl border border-base-600 bg-base-800/60 shadow-panel ${className}`}>
      {(title || action) && (
        <div className="flex items-center justify-between px-5 pt-4">
          <div>
            {title && <h3 className="text-sm font-semibold text-ink-100">{title}</h3>}
            {subtitle && <p className="mt-0.5 text-xs text-ink-500">{subtitle}</p>}
          </div>
          {action}
        </div>
      )}
      <div className="p-5">{children}</div>
    </div>
  );
}

export function StatCard({
  label,
  value,
  sublabel,
  accent = "text-ink-100",
}: {
  label: string;
  value: string;
  sublabel?: string;
  accent?: string;
}) {
  return (
    <div className="rounded-xl border border-base-600 bg-base-800/60 p-5 shadow-panel">
      <p className="text-xs font-medium uppercase tracking-wide text-ink-500">{label}</p>
      <p className={`mt-2 font-mono text-2xl font-semibold tabular ${accent}`}>{value}</p>
      {sublabel && <p className="mt-1 text-xs text-ink-500">{sublabel}</p>}
    </div>
  );
}

export function RiskBadge({ level }: { level: string }) {
  const color = riskColor(level);
  return (
    <span
      className="inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium"
      style={{ borderColor: `${color}55`, color, backgroundColor: `${color}14` }}
    >
      <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: color }} />
      {level}
    </span>
  );
}

export function PriorityBadge({ priority }: { priority: string }) {
  return <RiskBadge level={priority} />;
}

export function ProgressBar({ value, color }: { value: number; color?: string }) {
  return (
    <div className="h-1.5 w-full overflow-hidden rounded-full bg-base-600">
      <div
        className="h-full rounded-full"
        style={{ width: `${Math.min(100, Math.max(0, value))}%`, backgroundColor: color || "#22D3EE" }}
      />
    </div>
  );
}

export function Button({
  children,
  onClick,
  variant = "primary",
  disabled,
  type = "button",
  className = "",
}: {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: "primary" | "secondary" | "ghost";
  disabled?: boolean;
  type?: "button" | "submit";
  className?: string;
}) {
  const base = "inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition focus-ring disabled:opacity-50 disabled:cursor-not-allowed";
  const variants: Record<string, string> = {
    primary: "bg-brand-500 text-base-950 hover:bg-brand-400",
    secondary: "bg-base-700 text-ink-100 border border-base-500 hover:bg-base-600",
    ghost: "text-ink-300 hover:text-ink-100 hover:bg-base-700",
  };
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`${base} ${variants[variant]} ${className}`}
    >
      {children}
    </button>
  );
}

export function Loading({ label = "Loading..." }: { label?: string }) {
  return (
    <div className="flex h-64 flex-col items-center justify-center gap-3 text-ink-500">
      <div className="h-6 w-6 animate-spin rounded-full border-2 border-base-600 border-t-brand-500" />
      <p className="text-sm">{label}</p>
    </div>
  );
}

export function ErrorState({ message }: { message: string }) {
  return (
    <div className="flex h-64 flex-col items-center justify-center gap-2 rounded-xl border border-risk-critical/30 bg-risk-critical/5 text-center">
      <p className="text-sm font-medium text-risk-critical">Something went wrong</p>
      <p className="max-w-md text-xs text-ink-500">{message}</p>
    </div>
  );
}
