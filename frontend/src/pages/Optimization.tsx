import React, { useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";
import { api, OptimizationResult, formatINR } from "../lib/api";
import { Card, Button, StatCard, Loading } from "../components/ui";

export default function Optimization() {
  const [budget, setBudget] = useState<number>(1_00_00_000);
  const [result, setResult] = useState<OptimizationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runOptimization = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.runOptimization(budget);
      setResult(res);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const remaining = result ? result.budget - result.total_investment : 0;
  const chartData = result?.plan.map((p) => ({ name: p.name, cost: p.cost, reduction: p.risk_reduction })) ?? [];

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-xl font-semibold text-ink-100">Security Investment Optimization</h1>
        <p className="mt-1 max-w-2xl text-sm text-ink-500">
          Enter a security budget. The engine selects the combination of investments that maximizes total risk
          reduction without exceeding it.
        </p>
      </div>

      <Card title="Set Security Budget">
        <div className="flex flex-wrap items-end gap-4">
          <div>
            <label className="mb-1.5 block text-xs font-medium uppercase tracking-wide text-ink-500">
              Budget (INR)
            </label>
            <input
              type="number"
              min={0}
              step={100000}
              value={budget}
              onChange={(e) => setBudget(Math.max(0, Number(e.target.value)))}
              className="w-56 rounded-lg border border-base-600 bg-base-800 px-3 py-2.5 font-mono text-sm text-ink-100 focus-ring"
            />
            <p className="mt-1 text-xs text-ink-500">{formatINR(budget)}</p>
          </div>
          <div className="flex gap-2">
            {[50_00_000, 1_00_00_000, 1_50_00_000, 2_00_00_000].map((v) => (
              <button
                key={v}
                onClick={() => setBudget(v)}
                className="rounded-lg border border-base-600 bg-base-700/30 px-3 py-2 text-xs text-ink-300 hover:border-base-500"
              >
                {formatINR(v)}
              </button>
            ))}
          </div>
          <Button onClick={runOptimization} disabled={loading}>
            {loading ? "Optimizing..." : "Optimize Investment"}
          </Button>
        </div>
        {error && <p className="mt-3 text-xs text-risk-critical">{error}</p>}
      </Card>

      {loading && <Loading label="Solving budget-constrained optimization..." />}

      {result && !loading && (
        <>
          <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
            <StatCard label="Budget" value={formatINR(result.budget)} />
            <StatCard label="Total Investment" value={formatINR(result.total_investment)} accent="text-brand-400" />
            <StatCard label="Remaining Budget" value={formatINR(remaining)} />
            <StatCard label="ROSI" value={`${result.rosi_percent}%`} accent={result.rosi_percent >= 0 ? "text-risk-low" : "text-risk-critical"} sublabel="Return on Security Investment" />
          </div>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            <StatCard label="Risk Before" value={formatINR(result.risk_before)} accent="text-risk-high" />
            <StatCard label="Risk After" value={formatINR(result.risk_after)} accent="text-risk-medium" />
            <StatCard label="Risk Reduction" value={formatINR(result.risk_reduction)} accent="text-brand-400" />
          </div>

          <Card title="Recommended Investment Plan">
            {result.plan.length === 0 ? (
              <p className="text-sm text-ink-500">Budget too small to fund any investment in the catalog.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full min-w-[500px] border-collapse text-sm">
                  <thead>
                    <tr className="border-b border-base-600 text-left text-xs uppercase tracking-wide text-ink-500">
                      <th className="pb-2 pr-4 font-medium">Investment</th>
                      <th className="pb-2 pr-4 font-medium">Cost</th>
                      <th className="pb-2 pr-4 font-medium">Risk Reduction</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.plan.map((p) => (
                      <tr key={p.action_key} className="border-b border-base-700/60">
                        <td className="py-2.5 pr-4 text-ink-100">{p.name}</td>
                        <td className="py-2.5 pr-4 font-mono text-ink-300">{formatINR(p.cost)}</td>
                        <td className="py-2.5 pr-4 font-mono text-brand-400">{formatINR(p.risk_reduction)}</td>
                      </tr>
                    ))}
                    <tr>
                      <td className="pt-3 pr-4 font-medium text-ink-100">Total</td>
                      <td className="pt-3 pr-4 font-mono font-medium text-ink-100">{formatINR(result.total_investment)}</td>
                      <td className="pt-3 pr-4 font-mono font-medium text-brand-400">{formatINR(result.risk_reduction)}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            )}
          </Card>

          {chartData.length > 0 && (
            <Card title="Investment vs Risk Reduction">
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={chartData}>
                  <CartesianGrid stroke="#182338" vertical={false} />
                  <XAxis dataKey="name" tick={{ fill: "#8291AC", fontSize: 11 }} axisLine={{ stroke: "#182338" }} tickLine={false} interval={0} angle={-15} textAnchor="end" height={70} />
                  <YAxis tick={{ fill: "#8291AC", fontSize: 12 }} axisLine={false} tickLine={false} tickFormatter={(v) => formatINR(v)} width={70} />
                  <Tooltip
                    contentStyle={{ background: "#111A2E", border: "1px solid #334361", borderRadius: 8, fontSize: 12 }}
                    labelStyle={{ color: "#8291AC" }}
                    formatter={(v: number) => formatINR(v)}
                  />
                  <Bar dataKey="cost" name="Cost" fill="#5EEAD4" radius={[6, 6, 0, 0]} />
                  <Bar dataKey="reduction" name="Risk Reduction" fill="#22D3EE" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </Card>
          )}

          {result.unselected.length > 0 && (
            <Card title="Not Selected" subtitle="Excluded due to budget constraints">
              <div className="flex flex-wrap gap-2">
                {result.unselected.map((u) => (
                  <span key={u.action_key} className="rounded-full border border-base-600 bg-base-700/30 px-3 py-1.5 text-xs text-ink-400">
                    {u.name} — {formatINR(u.cost)}
                  </span>
                ))}
              </div>
            </Card>
          )}

          <Card>
            <p className="text-xs leading-relaxed text-ink-500">
              <span className="font-medium text-ink-300">Methodology note: </span>
              Investments are selected via a 0/1 knapsack optimization maximizing total risk reduction within budget.
              Combined reduction is capped at 85% of total EAL to reflect diminishing marginal benefit of overlapping
              controls. ROSI = (Risk Reduction − Investment Cost) / Investment Cost × 100. Prototype methodology, not
              an official SIH formula.
            </p>
          </Card>
        </>
      )}
    </div>
  );
}
