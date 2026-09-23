// Thin fetch wrapper for the FastAPI backend.
// In dev, Vite proxies /api -> http://localhost:8000 (see vite.config.ts).
// In prod, set VITE_API_BASE_URL to the deployed backend origin.

const API_BASE = (import.meta as any).env?.VITE_API_BASE_URL || "";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      /* ignore */
    }
    throw new Error(`API error (${res.status}): ${detail}`);
  }
  return res.json();
}

export interface DashboardData {
  organization: string;
  enterprise_risk_score: number;
  total_financial_exposure: number;
  expected_annual_loss: number;
  value_at_risk_95: number;
  critical_risk_count: number;
  high_risk_count: number;
  medium_risk_count: number;
  low_risk_count: number;
  potential_risk_reduction: number;
  security_budget: number;
  risk_trend: { month: string; eal: number }[];
  exposure_by_business_unit: { business_unit: string; exposure: number }[];
  top_risk_contributors: { asset: string; eal: number }[];
  risk_distribution: { level: string; count: number }[];
  risk_reduction_opportunities: { action: string; risk_reduction: number }[];
}

export interface AssetSummary {
  id: number;
  name: string;
  asset_type: string;
  business_unit: string;
  criticality: number;
  vulnerability_count: number;
  incident_count: number;
  control_effectiveness: number;
  incident_likelihood: number;
  financial_impact: number;
  expected_annual_loss: number;
  risk_score: number;
  risk_level: string;
}

export interface AssetDetail {
  id: number;
  name: string;
  asset_type: string;
  business_unit: string;
  criticality: number;
  control_effectiveness: number;
  records_at_risk: number;
  data_sensitivity: number;
  vulnerabilities: { id: number; cve_like_id: string; severity: string; cvss_score: number; description: string; patched: boolean }[];
  incidents: { id: number; incident_type: string; severity: string; financial_loss: number }[];
  controls: { id: number; control_name: string; implemented: boolean; effectiveness: number }[];
  risk: {
    incident_likelihood: number;
    financial_impact: number;
    expected_annual_loss: number;
    value_at_risk_95: number;
    risk_score: number;
    risk_level: string;
  } | null;
  impact_breakdown: Record<string, number>;
}

export interface RiskDriversData {
  top_risk_drivers: { driver: string; weight_percent: number }[];
  asset_risk_ranking: { asset: string; risk_score: number; risk_level: string; expected_annual_loss: number }[];
  methodology_note: string;
}

export interface Recommendation {
  id: number;
  asset_id: number;
  asset_name: string;
  action_key: string;
  problem: string;
  recommended_action: string;
  estimated_cost: number;
  estimated_risk_reduction: number;
  new_estimated_eal: number;
  priority: string;
  narrative: string;
}

export interface SimulationAction {
  action_key: string;
  name: string;
  description: string;
  cost: number;
}

export interface SimulationResult {
  action_key: string;
  action_name: string;
  delay_days: number;
  eal_before: number;
  eal_after: number;
  eal_after_with_delay: number;
  risk_reduction: number;
  risk_reduction_with_delay: number;
  investment_cost: number;
  delay_impact: number;
}

export interface OptimizationResult {
  budget: number;
  total_investment: number;
  risk_before: number;
  risk_after: number;
  risk_reduction: number;
  rosi_percent: number;
  plan: { action_key: string; name: string; cost: number; risk_reduction: number }[];
  unselected: { action_key: string; name: string; cost: number }[];
}

export interface ComplianceItem {
  id: number;
  finding: string;
  status: string;
  frameworks: string[];
  recommended_action: string;
}

export const api = {
  getDashboard: () => request<DashboardData>("/api/dashboard"),
  getAssets: () => request<AssetSummary[]>("/api/assets"),
  getAsset: (id: number) => request<AssetDetail>(`/api/assets/${id}`),
  getRiskDrivers: () => request<RiskDriversData>("/api/risks"),
  getRecommendations: () => request<Recommendation[]>("/api/recommendations"),
  getSimulationActions: () => request<SimulationAction[]>("/api/simulation/actions"),
  runSimulation: (action_key: string, delay_days: number) =>
    request<SimulationResult>("/api/simulation", {
      method: "POST",
      body: JSON.stringify({ action_key, delay_days }),
    }),
  runOptimization: (budget: number) =>
    request<OptimizationResult>("/api/optimization", {
      method: "POST",
      body: JSON.stringify({ budget }),
    }),
  getCompliance: () => request<ComplianceItem[]>("/api/compliance"),
  generateReport: async (): Promise<Blob> => {
    const res = await fetch(`${API_BASE}/api/reports`, { method: "POST" });
    if (!res.ok) throw new Error("Failed to generate report");
    return res.blob();
  },
};

export function formatINR(value: number): string {
  if (Math.abs(value) >= 1_00_00_000) return `₹${(value / 1_00_00_000).toFixed(2)} Cr`;
  if (Math.abs(value) >= 1_00_000) return `₹${(value / 1_00_000).toFixed(2)} L`;
  if (Math.abs(value) >= 1_000) return `₹${(value / 1_000).toFixed(1)}K`;
  return `₹${value.toFixed(0)}`;
}

export function riskColor(level: string): string {
  switch (level) {
    case "Critical":
      return "#EF4444";
    case "High":
      return "#FB7185";
    case "Medium":
      return "#FBBF24";
    default:
      return "#34D399";
  }
}
