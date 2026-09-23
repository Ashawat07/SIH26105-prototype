import React, { useEffect, useState } from "react";
import { api, Recommendation, formatINR } from "../lib/api";
import { Card, PriorityBadge, Loading, ErrorState } from "../components/ui";

export default function AIAdvisor() {
  const [recs, setRecs] = useState<Recommendation[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [assetFilter, setAssetFilter] = useState<string>("All assets");

  useEffect(() => {
    api.getRecommendations().then(setRecs).catch((e) => setError(e.message));
  }, []);

  if (error) return <ErrorState message={error} />;
  if (!recs) return <Loading label="Analyzing risk data and generating recommendations..." />;

  const assetNames = ["All assets", ...Array.from(new Set(recs.map((r) => r.asset_name)))];
  const filtered = assetFilter === "All assets" ? recs : recs.filter((r) => r.asset_name === assetFilter);

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-xl font-semibold text-ink-100">AI Security Advisor</h1>
          <p className="mt-1 max-w-2xl text-sm text-ink-500">
            Deterministic recommendations generated from the risk calculation engine — every cost and risk-reduction
            figure below comes from the backend, not from a language model guessing numbers.
          </p>
        </div>
        <select
          value={assetFilter}
          onChange={(e) => setAssetFilter(e.target.value)}
          className="rounded-lg border border-base-600 bg-base-800 px-3 py-2 text-sm text-ink-100 focus-ring"
        >
          {assetNames.map((n) => (
            <option key={n} value={n}>{n}</option>
          ))}
        </select>
      </div>

      {filtered.length === 0 ? (
        <Card><p className="text-sm text-ink-500">No open recommendations for this selection — controls already meet the effectiveness threshold.</p></Card>
      ) : (
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          {filtered.map((r) => (
            <Card key={r.id}>
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-xs text-ink-500">{r.asset_name}</p>
                  <h3 className="mt-0.5 text-sm font-semibold text-ink-100">{r.recommended_action}</h3>
                </div>
                <PriorityBadge priority={r.priority} />
              </div>

              <p className="mt-3 text-xs leading-relaxed text-ink-500">
                <span className="font-medium text-ink-300">Problem: </span>{r.problem}
              </p>

              <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
                <div className="rounded-lg border border-base-600 bg-base-700/30 p-3">
                  <p className="text-[11px] uppercase tracking-wide text-ink-500">Estimated Cost</p>
                  <p className="mt-1 font-mono font-medium text-ink-100">{formatINR(r.estimated_cost)}</p>
                </div>
                <div className="rounded-lg border border-base-600 bg-base-700/30 p-3">
                  <p className="text-[11px] uppercase tracking-wide text-ink-500">Risk Reduction</p>
                  <p className="mt-1 font-mono font-medium text-brand-400">{formatINR(r.estimated_risk_reduction)}</p>
                </div>
                <div className="rounded-lg border border-base-600 bg-base-700/30 p-3">
                  <p className="text-[11px] uppercase tracking-wide text-ink-500">New Estimated EAL</p>
                  <p className="mt-1 font-mono font-medium text-ink-100">{formatINR(r.new_estimated_eal)}</p>
                </div>
                <div className="rounded-lg border border-base-600 bg-base-700/30 p-3">
                  <p className="text-[11px] uppercase tracking-wide text-ink-500">Priority</p>
                  <p className="mt-1 text-ink-100">{r.priority}</p>
                </div>
              </div>

              <p className="mt-3 text-xs leading-relaxed text-ink-500">{r.narrative}</p>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
