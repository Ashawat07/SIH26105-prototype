import React, { useEffect, useState } from "react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, PieChart, Pie, Cell, Legend,
} from "recharts";
import { api, DashboardData, formatINR, riskColor } from "../lib/api";
import { Card, StatCard, Loading, ErrorState } from "../components/ui";

const CHART_GRID = "#182338";
const CHART_TEXT = "#8291AC";

function ChartTooltip({ active, payload, label, valueFormatter }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-lg border border-base-500 bg-base-800 px-3 py-2 text-xs shadow-panel">
      <p className="mb-1 text-ink-500">{label}</p>
      {payload.map((p: any, i: number) => (
        <p key={i} className="font-mono text-ink-100">
          {p.name}: {valueFormatter ? valueFormatter(p.value) : p.value}
        </p>
      ))}
    </div>
  );
}

export default function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getDashboard().then(setData).catch((e) => setError(e.message));
  }, []);

  if (error) return <ErrorState message={error} />;
  if (!data) return <Loading label="Loading executive dashboard..." />;

  const distributionColors: Record<string, string> = {
    Critical: riskColor("Critical"),
    High: riskColor("High"),
    Medium: riskColor("Medium"),
    Low: riskColor("Low"),
  };

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-xl font-semibold text-ink-100">Executive Risk Dashboard</h1>
        <p className="mt-1 text-sm text-ink-500">
          Cyber risk quantified in financial terms across {data.organization}, updated from the live asset dataset.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <StatCard label="Enterprise Risk Score" value={`${data.enterprise_risk_score}/100`} sublabel="Weighted average across all assets" />
        <StatCard label="Financial Exposure" value={formatINR(data.total_financial_exposure)} sublabel="Total single-loss exposure (SLE)" accent="text-brand-400" />
        <StatCard label="Expected Annual Loss" value={formatINR(data.expected_annual_loss)} sublabel="EAL = likelihood × impact" accent="text-risk-medium" />
        <StatCard label="Estimated VaR (95%)" value={formatINR(data.value_at_risk_95)} sublabel="Tail-risk annual loss estimate" accent="text-risk-high" />
        <StatCard label="Critical Risks" value={String(data.critical_risk_count)} sublabel="Assets scoring 81-100" accent="text-risk-critical" />
        <StatCard label="High Risks" value={String(data.high_risk_count)} sublabel="Assets scoring 61-80" accent="text-risk-high" />
        <StatCard label="Risk Reduction Opportunity" value={formatINR(data.potential_risk_reduction)} sublabel="From all open recommendations" accent="text-brand-400" />
        <StatCard label="Security Investment Budget" value={formatINR(data.security_budget)} sublabel="Annual allocation, illustrative" />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Card title="Expected Annual Loss Trend" subtitle="Illustrative 6-month trend converging to current EAL" className="lg:col-span-2">
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={data.risk_trend}>
              <CartesianGrid stroke={CHART_GRID} vertical={false} />
              <XAxis dataKey="month" tick={{ fill: CHART_TEXT, fontSize: 12 }} axisLine={{ stroke: CHART_GRID }} tickLine={false} />
              <YAxis tick={{ fill: CHART_TEXT, fontSize: 12 }} axisLine={false} tickLine={false} tickFormatter={(v) => formatINR(v)} width={70} />
              <Tooltip content={<ChartTooltip valueFormatter={formatINR} />} />
              <Line type="monotone" dataKey="eal" name="EAL" stroke="#22D3EE" strokeWidth={2.5} dot={{ r: 3, fill: "#22D3EE" }} />
            </LineChart>
          </ResponsiveContainer>
        </Card>

        <Card title="Risk Distribution" subtitle="Assets by risk level">
          <ResponsiveContainer width="100%" height={240}>
            <PieChart>
              <Pie
                data={data.risk_distribution}
                dataKey="count"
                nameKey="level"
                innerRadius={55}
                outerRadius={85}
                paddingAngle={3}
              >
                {data.risk_distribution.map((d, i) => (
                  <Cell key={i} fill={distributionColors[d.level] || "#334361"} stroke="none" />
                ))}
              </Pie>
              <Legend
                verticalAlign="bottom"
                height={36}
                formatter={(value) => <span style={{ color: CHART_TEXT, fontSize: 12 }}>{value}</span>}
              />
              <Tooltip content={<ChartTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card title="Financial Exposure by Business Unit">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={data.exposure_by_business_unit} layout="vertical" margin={{ left: 20 }}>
              <CartesianGrid stroke={CHART_GRID} horizontal={false} />
              <XAxis type="number" tick={{ fill: CHART_TEXT, fontSize: 12 }} axisLine={false} tickLine={false} tickFormatter={(v) => formatINR(v)} />
              <YAxis dataKey="business_unit" type="category" tick={{ fill: CHART_TEXT, fontSize: 12 }} axisLine={false} tickLine={false} width={130} />
              <Tooltip content={<ChartTooltip valueFormatter={formatINR} />} />
              <Bar dataKey="exposure" name="Exposure" fill="#5EEAD4" radius={[0, 6, 6, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card title="Top Risk Contributors" subtitle="By Expected Annual Loss">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={data.top_risk_contributors} layout="vertical" margin={{ left: 20 }}>
              <CartesianGrid stroke={CHART_GRID} horizontal={false} />
              <XAxis type="number" tick={{ fill: CHART_TEXT, fontSize: 12 }} axisLine={false} tickLine={false} tickFormatter={(v) => formatINR(v)} />
              <YAxis dataKey="asset" type="category" tick={{ fill: CHART_TEXT, fontSize: 12 }} axisLine={false} tickLine={false} width={130} />
              <Tooltip content={<ChartTooltip valueFormatter={formatINR} />} />
              <Bar dataKey="eal" name="EAL" fill="#FB7185" radius={[0, 6, 6, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      <Card title="Risk Reduction Opportunities" subtitle="Aggregated potential reduction by recommended action">
        <ResponsiveContainer width="100%" height={240}>
          <BarChart data={data.risk_reduction_opportunities}>
            <CartesianGrid stroke={CHART_GRID} vertical={false} />
            <XAxis dataKey="action" tick={{ fill: CHART_TEXT, fontSize: 11 }} axisLine={{ stroke: CHART_GRID }} tickLine={false} interval={0} angle={-15} textAnchor="end" height={70} />
            <YAxis tick={{ fill: CHART_TEXT, fontSize: 12 }} axisLine={false} tickLine={false} tickFormatter={(v) => formatINR(v)} width={70} />
            <Tooltip content={<ChartTooltip valueFormatter={formatINR} />} />
            <Bar dataKey="risk_reduction" name="Risk Reduction" fill="#22D3EE" radius={[6, 6, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </Card>
    </div>
  );
}
