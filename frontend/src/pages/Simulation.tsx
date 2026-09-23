import React, { useEffect, useState } from "react";
import { api, SimulationAction, SimulationResult, formatINR } from "../lib/api";
import { Card, Button, Loading, ErrorState, StatCard } from "../components/ui";

export default function Simulation() {
  const [actions, setActions] = useState<SimulationAction[] | null>(null);
  const [selected, setSelected] = useState<string>("");
  const [delayDays, setDelayDays] = useState<number>(0);
  const [result, setResult] = useState<SimulationResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    api.getSimulationActions().then((a) => {
      setActions(a);
      if (a.length) setSelected(a[0].action_key);
    }).catch((e) => setError(e.message));
  }, []);

  const runSimulation = async (withDelay: boolean) => {
    if (!selected) return;
    setRunning(true);
    setError(null);
    try {
      const res = await api.runSimulation(selected, withDelay ? delayDays : 0);
      setResult(res);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setRunning(false);
    }
  };

  if (error && !actions) return <ErrorState message={error} />;
  if (!actions) return <Loading label="Loading available security actions..." />;

  const selectedAction = actions.find((a) => a.action_key === selected);

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-xl font-semibold text-ink-100">What-if Simulation</h1>
        <p className="mt-1 max-w-2xl text-sm text-ink-500">
          Model how a single security investment changes organization-wide Expected Annual Loss, and see the cost of
          delaying remediation.
        </p>
      </div>

      <Card title="Select a Security Action">
        <div className="flex flex-wrap gap-2">
          {actions.map((a) => (
            <button
              key={a.action_key}
              onClick={() => { setSelected(a.action_key); setResult(null); }}
              className={`rounded-lg border px-4 py-2.5 text-left text-sm transition ${
                selected === a.action_key
                  ? "border-brand-500 bg-brand-500/10 text-brand-400"
                  : "border-base-600 bg-base-700/30 text-ink-300 hover:border-base-500"
              }`}
            >
              <p className="font-medium">{a.name}</p>
              <p className="mt-0.5 text-xs text-ink-500">Cost {formatINR(a.cost)}</p>
            </button>
          ))}
        </div>
        {selectedAction && (
          <p className="mt-3 text-xs text-ink-500">{selectedAction.description}</p>
        )}

        <div className="mt-5 flex flex-wrap items-center gap-4">
          <Button onClick={() => runSimulation(false)} disabled={running}>
            {running ? "Simulating..." : "Run Simulation"}
          </Button>

          <div className="flex items-center gap-2 text-sm text-ink-300">
            <span>Delay remediation by</span>
            <input
              type="number"
              min={0}
              step={30}
              value={delayDays}
              onChange={(e) => setDelayDays(Math.max(0, Number(e.target.value)))}
              className="w-20 rounded-lg border border-base-600 bg-base-800 px-2 py-1.5 text-center font-mono text-sm focus-ring"
            />
            <span>days</span>
            <Button variant="secondary" onClick={() => runSimulation(true)} disabled={running}>
              Simulate Delay
            </Button>
          </div>
        </div>

        {error && <p className="mt-3 text-xs text-risk-critical">{error}</p>}
      </Card>

      {result && (
        <>
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <Card title="Before" subtitle="Current organization-wide state">
              <div className="grid grid-cols-2 gap-3">
                <StatCard label="Expected Annual Loss" value={formatINR(result.eal_before)} />
                <StatCard label="Investment Cost" value={formatINR(result.investment_cost)} />
              </div>
            </Card>
            <Card
              title={result.delay_days > 0 ? `After — with ${result.delay_days} day delay` : "After Action"}
              subtitle={result.delay_days > 0 ? "Exposure compounds while remediation is postponed" : `Applying: ${result.action_name}`}
            >
              <div className="grid grid-cols-2 gap-3">
                <StatCard
                  label="New EAL"
                  value={formatINR(result.delay_days > 0 ? result.eal_after_with_delay : result.eal_after)}
                  accent="text-brand-400"
                />
                <StatCard
                  label="Risk Reduction"
                  value={formatINR(result.delay_days > 0 ? result.risk_reduction_with_delay : result.risk_reduction)}
                  accent="text-risk-medium"
                />
              </div>
            </Card>
          </div>

          {result.delay_days > 0 && (
            <Card title="Delay Impact">
              <p className="text-sm text-ink-300">
                Delaying <span className="font-medium text-ink-100">{result.action_name}</span> by{" "}
                <span className="font-mono text-ink-100">{result.delay_days}</span> days increases the exposure base
                by approximately <span className="font-mono font-medium text-risk-high">{formatINR(result.delay_impact)}</span> before
                the action is even applied — the prototype models a 4% exposure growth per 30 days of delay.
              </p>
            </Card>
          )}

          <Card>
            <p className="text-xs leading-relaxed text-ink-500">
              <span className="font-medium text-ink-300">Methodology note: </span>
              Risk reduction = current EAL × the selected action's risk-reduction factor. Delay impact compounds the
              EAL base at 4% per 30 days before the action is applied. This is the prototype's simplified simulation
              methodology, not an official SIH formula.
            </p>
          </Card>
        </>
      )}
    </div>
  );
}
