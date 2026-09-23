import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api, AssetDetail, formatINR, riskColor } from "../lib/api";
import { Card, StatCard, RiskBadge, Loading, ErrorState, Button, ProgressBar } from "../components/ui";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from "recharts";

const IMPACT_LABELS: Record<string, string> = {
  downtime_cost: "Downtime Cost",
  data_breach_cost: "Data Breach Cost",
  recovery_cost: "Recovery Cost",
  regulatory_cost: "Regulatory Cost",
  operational_loss: "Operational Loss",
};

export default function AssetDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [asset, setAsset] = useState<AssetDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    api.getAsset(Number(id)).then(setAsset).catch((e) => setError(e.message));
  }, [id]);

  if (error) return <ErrorState message={error} />;
  if (!asset) return <Loading label="Loading asset detail..." />;

  const impactData = Object.entries(asset.impact_breakdown)
    .filter(([k]) => IMPACT_LABELS[k])
    .map(([k, v]) => ({ name: IMPACT_LABELS[k], value: v }));

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <Button variant="ghost" onClick={() => navigate("/assets")} className="mb-2 -ml-3 px-3">
            ← Back to Assets
          </Button>
          <h1 className="text-xl font-semibold text-ink-100">{asset.name}</h1>
          <p className="mt-1 text-sm text-ink-500">{asset.asset_type} · {asset.business_unit}</p>
        </div>
        {asset.risk && <RiskBadge level={asset.risk.risk_level} />}
      </div>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <StatCard label="Risk Score" value={`${asset.risk?.risk_score ?? "-"}/100`} />
        <StatCard label="Incident Likelihood" value={`${Math.round((asset.risk?.incident_likelihood ?? 0) * 100)}%`} sublabel="Annualized probability" />
        <StatCard label="Financial Impact" value={formatINR(asset.risk?.financial_impact ?? 0)} sublabel="Single-loss expectancy" accent="text-brand-400" />
        <StatCard label="Expected Annual Loss" value={formatINR(asset.risk?.expected_annual_loss ?? 0)} accent="text-risk-medium" />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Card title="Financial Impact Breakdown" className="lg:col-span-2">
          <ResponsiveContainer width="100%" height={230}>
            <BarChart data={impactData} layout="vertical" margin={{ left: 20 }}>
              <CartesianGrid stroke="#182338" horizontal={false} />
              <XAxis type="number" tick={{ fill: "#8291AC", fontSize: 12 }} axisLine={false} tickLine={false} tickFormatter={(v) => formatINR(v)} />
              <YAxis dataKey="name" type="category" tick={{ fill: "#8291AC", fontSize: 12 }} axisLine={false} tickLine={false} width={120} />
              <Tooltip
                contentStyle={{ background: "#111A2E", border: "1px solid #334361", borderRadius: 8, fontSize: 12 }}
                labelStyle={{ color: "#8291AC" }}
                formatter={(v: number) => formatINR(v)}
              />
              <Bar dataKey="value" radius={[0, 6, 6, 0]}>
                {impactData.map((_, i) => <Cell key={i} fill="#22D3EE" />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card title="Asset Profile">
          <dl className="flex flex-col gap-3 text-sm">
            <div className="flex items-center justify-between">
              <dt className="text-ink-500">Criticality</dt>
              <dd className="font-mono text-ink-100">{asset.criticality}/5</dd>
            </div>
            <div className="flex items-center justify-between">
              <dt className="text-ink-500">Data Sensitivity</dt>
              <dd className="font-mono text-ink-100">{asset.data_sensitivity}/5</dd>
            </div>
            <div className="flex items-center justify-between">
              <dt className="text-ink-500">Records at Risk</dt>
              <dd className="font-mono text-ink-100">{asset.records_at_risk.toLocaleString("en-IN")}</dd>
            </div>
            <div>
              <div className="mb-1 flex items-center justify-between">
                <dt className="text-ink-500">Control Effectiveness</dt>
                <dd className="font-mono text-ink-100">{Math.round(asset.control_effectiveness * 100)}%</dd>
              </div>
              <ProgressBar value={asset.control_effectiveness * 100} color="#5EEAD4" />
            </div>
            <div>
              <div className="mb-1 flex items-center justify-between">
                <dt className="text-ink-500">Value at Risk (95%)</dt>
                <dd className="font-mono text-ink-100">{formatINR(asset.risk?.value_at_risk_95 ?? 0)}</dd>
              </div>
            </div>
          </dl>
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Card title="Vulnerabilities" subtitle={`${asset.vulnerabilities.length} identified`}>
          <ul className="flex flex-col gap-3">
            {asset.vulnerabilities.map((v) => (
              <li key={v.id} className="rounded-lg border border-base-600 bg-base-700/30 p-3">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs text-ink-500">{v.cve_like_id}</span>
                  <span className="rounded-full px-2 py-0.5 text-[11px] font-medium" style={{ color: riskColor(v.severity === "Critical" || v.severity === "High" ? v.severity : v.severity === "Medium" ? "Medium" : "Low"), backgroundColor: `${riskColor(v.severity)}18` }}>
                    {v.severity} · CVSS {v.cvss_score}
                  </span>
                </div>
                <p className="mt-1.5 text-sm text-ink-300">{v.description}</p>
                <p className="mt-1 text-xs text-ink-500">{v.patched ? "Patched" : "Open — not yet remediated"}</p>
              </li>
            ))}
          </ul>
        </Card>

        <Card title="Incident History" subtitle={`${asset.incidents.length} in the last 12 months`}>
          {asset.incidents.length === 0 ? (
            <p className="text-sm text-ink-500">No recorded incidents in the last 12 months.</p>
          ) : (
            <ul className="flex flex-col gap-3">
              {asset.incidents.map((inc) => (
                <li key={inc.id} className="rounded-lg border border-base-600 bg-base-700/30 p-3">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium text-ink-100">{inc.incident_type}</p>
                    <span className="text-[11px] font-medium" style={{ color: riskColor(inc.severity) }}>{inc.severity}</span>
                  </div>
                  <p className="mt-1 text-xs text-ink-500">Loss recorded: {formatINR(inc.financial_loss)}</p>
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card title="Security Controls">
          <ul className="flex flex-col gap-3">
            {asset.controls.map((c) => (
              <li key={c.id} className="flex items-center justify-between rounded-lg border border-base-600 bg-base-700/30 p-3">
                <div>
                  <p className="text-sm font-medium text-ink-100">{c.control_name}</p>
                  <p className="text-xs text-ink-500">{c.implemented ? "Implemented" : "Not implemented"}</p>
                </div>
                <div className="w-16">
                  <ProgressBar value={c.effectiveness * 100} color={c.implemented ? "#5EEAD4" : "#FB7185"} />
                </div>
              </li>
            ))}
          </ul>
        </Card>
      </div>
    </div>
  );
}
