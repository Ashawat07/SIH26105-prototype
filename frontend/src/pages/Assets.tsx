import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, AssetSummary, formatINR } from "../lib/api";
import { Card, RiskBadge, Loading, ErrorState, ProgressBar } from "../components/ui";
import { riskColor } from "../lib/api";

export default function Assets() {
  const [assets, setAssets] = useState<AssetSummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    api.getAssets().then(setAssets).catch((e) => setError(e.message));
  }, []);

  if (error) return <ErrorState message={error} />;
  if (!assets) return <Loading label="Loading asset inventory..." />;

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-xl font-semibold text-ink-100">Asset & Risk Inventory</h1>
        <p className="mt-1 text-sm text-ink-500">{assets.length} assets assessed. Click any asset to see its detailed risk breakdown.</p>
      </div>

      <Card>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[900px] border-collapse text-sm">
            <thead>
              <tr className="border-b border-base-600 text-left text-xs uppercase tracking-wide text-ink-500">
                <th className="pb-3 pr-4 font-medium">Asset</th>
                <th className="pb-3 pr-4 font-medium">Business Unit</th>
                <th className="pb-3 pr-4 font-medium">Criticality</th>
                <th className="pb-3 pr-4 font-medium">Vulns</th>
                <th className="pb-3 pr-4 font-medium">Incidents</th>
                <th className="pb-3 pr-4 font-medium">Control Effectiveness</th>
                <th className="pb-3 pr-4 font-medium">Likelihood</th>
                <th className="pb-3 pr-4 font-medium">Financial Impact</th>
                <th className="pb-3 pr-4 font-medium">EAL</th>
                <th className="pb-3 pr-4 font-medium">Risk Level</th>
              </tr>
            </thead>
            <tbody>
              {assets.map((a) => (
                <tr
                  key={a.id}
                  onClick={() => navigate(`/assets/${a.id}`)}
                  className="cursor-pointer border-b border-base-700/60 transition hover:bg-base-700/40"
                >
                  <td className="py-3 pr-4">
                    <p className="font-medium text-ink-100">{a.name}</p>
                    <p className="text-xs text-ink-500">{a.asset_type}</p>
                  </td>
                  <td className="py-3 pr-4 text-ink-300">{a.business_unit}</td>
                  <td className="py-3 pr-4 text-ink-300">{a.criticality}/5</td>
                  <td className="py-3 pr-4 text-ink-300">{a.vulnerability_count}</td>
                  <td className="py-3 pr-4 text-ink-300">{a.incident_count}</td>
                  <td className="py-3 pr-4">
                    <div className="flex items-center gap-2">
                      <div className="w-20"><ProgressBar value={a.control_effectiveness * 100} color="#5EEAD4" /></div>
                      <span className="font-mono text-xs text-ink-500">{Math.round(a.control_effectiveness * 100)}%</span>
                    </div>
                  </td>
                  <td className="py-3 pr-4 font-mono text-ink-300">{Math.round(a.incident_likelihood * 100)}%</td>
                  <td className="py-3 pr-4 font-mono text-ink-100">{formatINR(a.financial_impact)}</td>
                  <td className="py-3 pr-4 font-mono font-medium" style={{ color: riskColor(a.risk_level) }}>{formatINR(a.expected_annual_loss)}</td>
                  <td className="py-3 pr-4"><RiskBadge level={a.risk_level} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
