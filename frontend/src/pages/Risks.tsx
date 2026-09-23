import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from "recharts";
import { api, RiskDriversData, formatINR, riskColor } from "../lib/api";
import { Card, RiskBadge, Loading, ErrorState } from "../components/ui";

export default function Risks() {
  const [data, setData] = useState<RiskDriversData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    api.getRiskDrivers().then(setData).catch((e) => setError(e.message));
  }, []);

  if (error) return <ErrorState message={error} />;
  if (!data) return <Loading label="Loading risk drivers..." />;

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-xl font-semibold text-ink-100">Risk Drivers</h1>
        <p className="mt-1 text-sm text-ink-500">Why the organization's risk is high, and which assets contribute most.</p>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card title="Top Risk Drivers" subtitle="Organization-wide, weighted by asset criticality">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data.top_risk_drivers} layout="vertical" margin={{ left: 10 }}>
              <CartesianGrid stroke="#182338" horizontal={false} />
              <XAxis type="number" tick={{ fill: "#8291AC", fontSize: 12 }} axisLine={false} tickLine={false} tickFormatter={(v) => `${v}%`} />
              <YAxis dataKey="driver" type="category" tick={{ fill: "#8291AC", fontSize: 11 }} axisLine={false} tickLine={false} width={190} />
              <Tooltip
                contentStyle={{ background: "#111A2E", border: "1px solid #334361", borderRadius: 8, fontSize: 12 }}
                labelStyle={{ color: "#8291AC" }}
                formatter={(v: number) => `${v}%`}
              />
              <Bar dataKey="weight_percent" name="Weight" radius={[0, 6, 6, 0]}>
                {data.top_risk_drivers.map((_, i) => <Cell key={i} fill="#22D3EE" />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card title="Asset Risk Ranking" subtitle="Click an asset to view full detail">
          <ul className="flex flex-col gap-2.5 max-h-[300px] overflow-y-auto pr-1">
            {data.asset_risk_ranking.map((a, i) => (
              <li
                key={i}
                onClick={() => navigate("/assets")}
                className="flex cursor-pointer items-center justify-between rounded-lg border border-base-600 bg-base-700/30 p-3 transition hover:bg-base-700/60"
              >
                <div>
                  <p className="text-sm font-medium text-ink-100">{a.asset}</p>
                  <p className="mt-0.5 text-xs text-ink-500">EAL {formatINR(a.expected_annual_loss)}</p>
                </div>
                <div className="flex items-center gap-3">
                  <span className="font-mono text-sm tabular" style={{ color: riskColor(a.risk_level) }}>{a.risk_score}</span>
                  <RiskBadge level={a.risk_level} />
                </div>
              </li>
            ))}
          </ul>
        </Card>
      </div>

      <Card>
        <p className="text-xs leading-relaxed text-ink-500">
          <span className="font-medium text-ink-300">Methodology note: </span>
          {data.methodology_note}
        </p>
      </Card>
    </div>
  );
}
