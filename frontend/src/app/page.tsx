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
      setHistory((prev) =>
        [
          {
            id: `${Date.now()}`,
            at: new Date().toLocaleTimeString(),
            request: payload,
            result: data,
          },
          ...prev,
        ].slice(0, 20),
      );
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

  function exportPdf() {
    window.print();
  }

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

  return (
    <main className="page">
      <header className="header">
        <h1>Fertilizer Recommendation System</h1>
        <p className="subtitle">
          Decision-support prototype designed for CAR (Cordillera
          Administrative Region) produce and land conditions.
        </p>
      </header>

      {catalogError && (
        <p className="error-banner" role="alert">
          Could not reach the API: {catalogError}
        </p>
      )}

      {!catalogError && !catalog && <p>Loading catalog…</p>}

      {catalog && (
        <form className="card form" onSubmit={submit}>
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
        <p className="error-banner" role="alert">
          {error}
        </p>
      )}

      {result && (
        <section className="card results" id="results">
          <div className="results-header">
            <h2>
              Recommendations — {result.selected_crop_label} (
              {result.raw_area} {result.unit_label})
            </h2>
            <button type="button" onClick={exportPdf}>
              Export PDF
            </button>
          </div>

          <p className="npk-targets">
            Target per hectare: N {result.base_targets_per_ha["N"]} · P{" "}
            {result.base_targets_per_ha["P"]} · K{" "}
            {result.base_targets_per_ha["K"]} | Total for plot: N{" "}
            {result.total_base["N"]} · P {result.total_base["P"]} · K{" "}
            {result.total_base["K"]}
          </p>

          <div
            className={`ph-box ph-${result.ph_result.ph_status}`}
            role="status"
          >
            <strong>Soil pH ({result.ph_result.soil_ph}):</strong>{" "}
            {result.ph_result.recommendation_message}
            {result.ph_result.borderline_warning &&
              result.ph_result.borderline_message && (
                <p className="ph-warning">
                  {result.ph_result.borderline_message}
                </p>
              )}
          </div>

          {result.inventory_check && !result.inventory_check.valid && (
            <p className="ph-warning" role="alert">
              Selected inventory issue: {result.inventory_check.reason}
            </p>
          )}
          {result.inventory_sufficiency &&
            result.inventory_sufficiency.missing_nutrients.length > 0 && (
              <p className="ph-warning">
                Your selection does not cover:{" "}
                {result.inventory_sufficiency.missing_nutrients.join(", ")}.
              </p>
            )}

          {result.farmer_selected_mix && (
            <>
              <h3>Your selected fertilizers</h3>
              {renderMix(result.farmer_selected_mix)}
            </>
          )}

          <h3>Standard recommendations</h3>
          {renderMix(result.standard_mix)}

          <p className="disclaimer">
            Disclaimer: This tool is a decision-support prototype designed for
            CAR produce and land conditions. Results are educational guidance
            only — consult a qualified agriculturist before applying fertilizer.
          </p>
        </section>
      )}

      {history.length > 0 && (
        <section className="card history no-print">
          <h2>Session history</h2>
          <p className="history-note">
            History is stored only in this browser session and is lost when the
            tab closes. Export results as PDF to keep them.
          </p>
          <ul>
            {history.map((entry) => (
              <li key={entry.id}>
                <button
                  type="button"
                  onClick={() => setResult(entry.result)}
                >
                  {entry.at}: {entry.request.crop_label} — {entry.request.soil_ph} pH,{" "}
                  {entry.request.raw_area} sqm
                </button>
              </li>
            ))}
          </ul>
        </section>
      )}
    </main>
  );
}
