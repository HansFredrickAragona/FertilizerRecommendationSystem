"use client";

import { useEffect, useState } from "react";
import {
  fetchCatalog,
  fetchRecommendation,
  type RecommendationResponse,
} from "@/lib/api";

const NPK_LEVELS = ["Low", "Medium", "High"] as const;
const AREA_UNITS = ["Square Meters (sqm)", "Hectares (ha)"] as const;

type HistoryEntry = {
  id: string;
  at: string;
  request: Parameters<typeof fetchRecommendation>[0];
  result: RecommendationResponse;
};

function renderMix(mix: RecommendationResponse["standard_mix"]) {
  if (!mix || mix.length === 0) {
    return <p>No combinations found.</p>;
  }
  return (
    <table className="mix-table">
      <thead>
        <tr>
          <th>Source</th>
          <th>Prescription</th>
          <th>Total (kg)</th>
          <th>Sacks</th>
        </tr>
      </thead>
      <tbody>
        {mix.map((entry) => (
          <tr key={entry.Source}>
            <td>{entry.Source}</td>
            <td>
              <ul>
                {entry.Prescription.map((line) => (
                  <li key={line}>{line.trim()}</li>
                ))}
              </ul>
            </td>
            <td>{entry["Total Weight"].toFixed(2)}</td>
            <td>{entry["Total Sacks"].toFixed(3)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function ResultCard({ result }: { result: RecommendationResponse }) {
  return (
    <section className="card results">
      <h2>
        Recommendations — {result.selected_crop_label} ({result.raw_area}{" "}
        {result.unit_label})
      </h2>

      <p className="npk-targets">
        Target per hectare: N {result.base_targets_per_ha["N"]} · P{" "}
        {result.base_targets_per_ha["P"]} · K {result.base_targets_per_ha["K"]}{" "}
        | Total for plot: N {result.total_base["N"]} · P{" "}
        {result.total_base["P"]} · K {result.total_base["K"]}
      </p>

      <div className={`ph-box ph-${result.ph_result.ph_status}`} role="status">
        <strong>Soil pH ({result.ph_result.soil_ph}):</strong>{" "}
        {result.ph_result.recommendation_message}
        {result.ph_result.borderline_warning &&
          result.ph_result.borderline_message && (
            <p className="ph-warning">
              {result.ph_result.borderline_message}
            </p>
          )}
      </div>

      {result.selection_status !== "none" && (
        <div
          className={`selection-banner selection-${result.selection_status}`}
          role="alert"
        >
          {result.selection_status === "sufficient" && (
            <p>
              <strong>Good news:</strong> your selected fertilizers (
              {result.user_inventory.map((f) => f.name).join(", ")}) can fully
              meet the NPK targets on their own.
            </p>
          )}
          {result.selection_status === "supplementable" && (
            <>
              <p>
                <strong>Notice:</strong> your selected fertilizers (
                {result.user_inventory.map((f) => f.name).join(", ")}) cannot
                fulfill the NPK targets alone, but they can be combined with
                one or more additional fertilizers. See the supplemented
                combinations below.
              </p>
              {result.inventory_sufficiency.missing_nutrients.length > 0 && (
                <p>
                  Your selection does not cover:{" "}
                  {result.inventory_sufficiency.missing_nutrients.join(", ")}.
                </p>
              )}
            </>
          )}
          {result.selection_status === "insufficient" && (
            <p>
              <strong>Warning:</strong> your selected fertilizers (
              {result.user_inventory.map((f) => f.name).join(", ")}) are not
              sufficient to fulfill the NPK targets, even with supplements.
              Please review the standard recommendations instead.
              {result.inventory_sufficiency.missing_nutrients.length > 0 && (
                <>
                  {" "}
                  Missing coverage:{" "}
                  {result.inventory_sufficiency.missing_nutrients.join(", ")}.
                </>
              )}
            </p>
          )}
        </div>
      )}

      {result.farmer_selected_mix.length > 0 && (
        <>
          <h3>Your selected fertilizers</h3>
          {renderMix(result.farmer_selected_mix)}
        </>
      )}

      {result.farmer_supplemented_mix.length > 0 && (
        <>
          <h3>Your selections + supplemental fertilizers</h3>
          <p className="section-note">
            Ordered by the most use of your selected fertilizers first, then by
            lowest total weight.
          </p>
          {renderMix(result.farmer_supplemented_mix)}
        </>
      )}

      <h3>Standard recommendations</h3>
      {renderMix(result.standard_mix)}

      <p className="disclaimer">
        Disclaimer: This tool is a decision-support prototype designed for CAR
        produce and land conditions. Results are educational guidance only —
        consult a qualified agriculturist before applying fertilizer.
      </p>
    </section>
  );
}

export default function Home() {
  const [catalog, setCatalog] = useState<Awaited<
    ReturnType<typeof fetchCatalog>
  > | null>(null);
  const [catalogError, setCatalogError] = useState<string | null>(null);

  const [cropLabel, setCropLabel] = useState("");
  const [nStatus, setNStatus] = useState<string>("Low");
  const [pStatus, setPStatus] = useState<string>("Low");
  const [kStatus, setKStatus] = useState<string>("Low");
  const [soilPh, setSoilPh] = useState("6.5");
  const [rawArea, setRawArea] = useState("500");
  const [areaUnit, setAreaUnit] = useState<string>(AREA_UNITS[0]);
  const [selectedFertilizers, setSelectedFertilizers] = useState<string[]>([]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<RecommendationResponse | null>(null);
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [selectedHistoryIds, setSelectedHistoryIds] = useState<Set<string>>(
    new Set(),
  );
  const [printQueue, setPrintQueue] = useState<HistoryEntry[] | null>(null);

  useEffect(() => {
    fetchCatalog()
      .then((data) => {
        setCatalog(data);
        if (data.crops.length > 0) setCropLabel(data.crops[0]);
      })
      .catch((exc) => setCatalogError(String(exc)));
  }, []);

  useEffect(() => {
    if (history.length === 0) return;
    const handler = (event: BeforeUnloadEvent) => {
      event.preventDefault();
    };
    window.addEventListener("beforeunload", handler);
    return () => window.removeEventListener("beforeunload", handler);
  }, [history]);

  useEffect(() => {
    if (!printQueue) return;
    const handler = () => setPrintQueue(null);
    window.addEventListener("afterprint", handler);
    return () => window.removeEventListener("afterprint", handler);
  }, [printQueue]);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const payload = {
        crop_label: cropLabel,
        n_status: nStatus,
        p_status: pStatus,
        k_status: kStatus,
        soil_ph: Number.parseFloat(soilPh),
        raw_area: Number.parseFloat(rawArea),
        area_unit: areaUnit,
        selected_inventory_names:
          selectedFertilizers.length > 0 ? selectedFertilizers : undefined,
      };
      const data = await fetchRecommendation(payload);
      setResult(data);
      const entry: HistoryEntry = {
        id: `${Date.now()}`,
        at: new Date().toLocaleTimeString(),
        request: payload,
        result: data,
      };
      setHistory((prev) => [entry, ...prev].slice(0, 20));
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : String(exc));
    } finally {
      setLoading(false);
    }
  }

  function toggleFertilizer(name: string) {
    setSelectedFertilizers((prev) =>
      prev.includes(name)
        ? prev.filter((item) => item !== name)
        : [...prev, name],
    );
  }

  function toggleHistorySelection(id: string) {
    setSelectedHistoryIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  }

  function exportSessions(entries: HistoryEntry[]) {
    if (entries.length === 0) return;
    setPrintQueue(entries);
    setTimeout(() => window.print(), 100);
  }

  function entryLabel(entry: HistoryEntry) {
    return `${entry.request.crop_label} — ${entry.request.soil_ph} pH, ${entry.request.raw_area} ${entry.request.area_unit.includes("Hectare") ? "ha" : "sqm"}, ${entry.request.selected_inventory_names?.length ?? 0} selected`;
  }

  return (
    <main className="page">
      <header className="header no-print">
        <h1>Fertilizer Recommendation System</h1>
        <p className="subtitle">
          Decision-support prototype designed for CAR (Cordillera
          Administrative Region) produce and land conditions.
        </p>
      </header>

      {catalogError && (
        <p className="error-banner no-print" role="alert">
          Could not reach the API: {catalogError}
        </p>
      )}

      {!catalogError && !catalog && <p>Loading catalog…</p>}

      {catalog && (
        <form className="card form no-print" onSubmit={submit}>
          <label>
            Crop
            <select
              value={cropLabel}
              onChange={(e) => setCropLabel(e.target.value)}
              required
            >
              {catalog.crops.map((crop) => (
                <option key={crop} value={crop}>
                  {crop}
                </option>
              ))}
            </select>
          </label>

          <div className="row">
            {(
              [
                ["Nitrogen (N)", nStatus, setNStatus],
                ["Phosphorus (P)", pStatus, setPStatus],
                ["Potassium (K)", kStatus, setKStatus],
              ] as const
            ).map(([label, value, setter]) => (
              <label key={label}>
                {label} status
                <select
                  value={value}
                  onChange={(e) => setter(e.target.value)}
                >
                  {NPK_LEVELS.map((level) => (
                    <option key={level}>{level}</option>
                  ))}
                </select>
              </label>
            ))}
          </div>

          <div className="row">
            <label>
              Soil pH
              <input
                type="number"
                step="0.1"
                min="0"
                max="14"
                value={soilPh}
                onChange={(e) => setSoilPh(e.target.value)}
                required
              />
            </label>
            <label>
              Area
              <input
                type="number"
                step="any"
                min="0"
                value={rawArea}
                onChange={(e) => setRawArea(e.target.value)}
                required
              />
            </label>
            <label>
              Unit
              <select
                value={areaUnit}
                onChange={(e) => setAreaUnit(e.target.value)}
              >
                {AREA_UNITS.map((unit) => (
                  <option key={unit}>{unit}</option>
                ))}
              </select>
            </label>
          </div>

          <fieldset>
            <legend>Farmer-selected fertilizers (optional)</legend>
            <div className="checkbox-grid">
              {catalog.fertilizers.map((fertilizer) => (
                <label key={fertilizer.name} className="checkbox-item">
                  <input
                    type="checkbox"
                    checked={selectedFertilizers.includes(fertilizer.name)}
                    onChange={() => toggleFertilizer(fertilizer.name)}
                  />
                  {fertilizer.name} ({fertilizer.n}-{fertilizer.p}-
                  {fertilizer.k})
                </label>
              ))}
            </div>
          </fieldset>

          <button type="submit" disabled={loading}>
            {loading ? "Calculating…" : "Get recommendation"}
          </button>
        </form>
      )}

      {error && (
        <p className="error-banner no-print" role="alert">
          {error}
        </p>
      )}

      {result && !printQueue && (
        <div className="results-wrapper">
          <ResultCard result={result} />
        </div>
      )}

      {history.length > 0 && (
        <section className="card history no-print">
          <h2>Session history</h2>
          <p className="history-note">
            History is stored only in this browser session and is lost when the
            tab closes. Select sessions below to export them as PDF.
          </p>
          <ul>
            {history.map((entry) => (
              <li key={entry.id} className="history-item">
                <label className="history-select">
                  <input
                    type="checkbox"
                    checked={selectedHistoryIds.has(entry.id)}
                    onChange={() => toggleHistorySelection(entry.id)}
                  />
                  <span>
                    {entry.at}: {entryLabel(entry)}
                  </span>
                </label>
                <span className="history-actions">
                  <button
                    type="button"
                    onClick={() => setResult(entry.result)}
                  >
                    View
                  </button>
                  <button
                    type="button"
                    onClick={() => exportSessions([entry])}
                  >
                    Export
                  </button>
                </span>
              </li>
            ))}
          </ul>
          <div className="history-bulk">
            <button
              type="button"
              disabled={selectedHistoryIds.size === 0}
              onClick={() =>
                exportSessions(
                  history.filter((entry) => selectedHistoryIds.has(entry.id)),
                )
              }
            >
              Export selected ({selectedHistoryIds.size})
            </button>
            <button type="button" onClick={() => exportSessions(history)}>
              Export all ({history.length})
            </button>
          </div>
        </section>
      )}

      {printQueue && (
        <div className="print-area">
          <h1>Fertilizer Recommendation System — Exported Results</h1>
          <p>
            Exported {new Date().toLocaleString()} · {printQueue.length}{" "}
            session{printQueue.length > 1 ? "s" : ""}
          </p>
          {printQueue.map((entry) => (
            <div key={entry.id} className="print-entry">
              <p className="print-entry-label">
                Session at {entry.at}: {entryLabel(entry)}
              </p>
              <ResultCard result={entry.result} />
            </div>
          ))}
        </div>
      )}
    </main>
  );
}
