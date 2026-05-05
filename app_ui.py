from app_final import build_recommendation, load_assets, THESIS_CROP_MAP
import streamlit as st
import pandas as pd


def run_ui():
    st.set_page_config(page_title="Rule-Based NPK + pH", layout="centered")
    st.title("🌱 Fertilizer Recommendation Engine")

    try:
        inventory, _, _, _= load_assets()

        with st.sidebar:
            st.header("1. Land Information")
            unit = st.radio("Select Area Unit", ["Square Meters (sqm)", "Hectares (ha)"])
            raw_area = st.number_input(
                f"Total Area ({unit})",
                min_value=1.0,
                value=500.0 if "sqm" in unit else 1.0,
            )

            st.write("---")
            st.header("2. Soil & Crop Data")
            selected_crop_label = st.selectbox("Select Crop", options=list(THESIS_CROP_MAP.keys()))
            n_lvl = st.selectbox("Nitrogen (N) Status", options=["Low", "Medium", "High"])
            p_lvl = st.selectbox("Phosphorus (P) Status", options=["Low", "Medium", "High"])
            k_lvl = st.selectbox("Potassium (K) Status", options=["Low", "Medium", "High"])
            soil_ph = st.number_input(
                "Soil pH", min_value=0.0, max_value=14.0, value=5.5, step=0.1
            )

            st.write("---")
            st.header("3. Inventory Management")
            with st.expander("🛒 Plan Your Purchase / Select Inventory", expanded=True):
                fert_names = [f["name"] for f in inventory]
                user_selection = st.multiselect(
                    "Select fertilizers you plan to buy or use:",
                    options=fert_names,
                    default=[],
                    help="Start typing to search for fertilizers like Urea, 14-14-14, etc.",
                )

        if st.button("Calculate Prescription", type="primary"):
            try:
                result = build_recommendation(
                    crop_label=selected_crop_label,
                    n_status=n_lvl,
                    p_status=p_lvl,
                    k_status=k_lvl,
                    soil_ph=soil_ph,
                    raw_area=raw_area,
                    area_unit=unit,
                    selected_inventory_names=user_selection,
                )
            except ValueError as ve:
                st.error(f"❌ Configuration Error: {ve}")
                return

            unit_label   = result["unit_label"]
            base_targets = result["base_targets_per_ha"]
            total_base   = result["total_base"]
            ph_res       = result["ph_result"]
            inv_check    = result["inventory_check"]
            inv_suff     = result["inventory_sufficiency"]
            standard_mix = result["standard_mix"]

            st.success(f"✅ Results for {raw_area} {unit}")

            # ── NUTRIENT BASIS ────────────────────────────────────────────────
            with st.expander("📊 View Nutrient Basis (Reference Rates)", expanded=False):
                st.markdown(
                    f"**Crop:** {selected_crop_label} | "
                    f"**Soil Status:** N:{n_lvl}, P:{p_lvl}, K:{k_lvl}"
                )
                st.write("Standard recommendation per hectare (Source: crop_npk_rules.json):")
                ref_col1, ref_col2, ref_col3 = st.columns(3)
                ref_col1.metric("Target N",    f"{base_targets['N']} kg/ha")
                ref_col2.metric("Target P₂O₅", f"{base_targets['P']} kg/ha")
                ref_col3.metric("Target K₂O",  f"{base_targets['K']} kg/ha")

            # ── 1. SOIL pH ASSESSMENT ─────────────────────────────────────────
            st.subheader("1. Soil Condition Assessment")

            ph_action           = ph_res.get("ph_action", "none")
            borderline_warning  = ph_res.get("borderline_warning", False)
            recommendation_msg  = ph_res.get("recommendation_message", "")
            borderline_msg      = ph_res.get("borderline_message", None)
            perfect_ph          = ph_res.get("perfect_ph", 6.5)

            if ph_action == "liming_required":
                st.error(f"⚠️ **Soil pH: {soil_ph} — Liming Required**")
                st.write(recommendation_msg)
            elif ph_action == "gypsum_recommended":
                st.warning(f"⚠️ **Soil pH: {soil_ph} — Gypsum Recommended**")
                st.write(recommendation_msg)
            elif borderline_warning:
                st.warning(f"⚠️ **Soil pH: {soil_ph} — Borderline Warning**")
                st.write(borderline_msg)
            else:
                st.success(f"✅ **Soil pH: {soil_ph} — Within Acceptable Range**")
                st.write(recommendation_msg)

            st.write(f"**Ideal pH:** {perfect_ph} &nbsp;|&nbsp; **Acceptable Range:** 5.1 – 7.4")
            st.divider()

            # ── INVENTORY SUITABILITY REPORT ──────────────────────────────────
            st.subheader("Inventory Suitability Report")

            if not user_selection:
                # No fertilizers chosen at all — skip detailed check
                st.info("ℹ️ No fertilizers selected. Add items from the sidebar to see a suitability report.")
            elif inv_check["valid"]:
                st.info(
                    f"✅ **Status: Sufficient.** Your inventory can fulfill the "
                    f"**{raw_area} {unit}** requirements."
                )
                unused = inv_check.get("unused", [])
                if unused:
                    st.warning(f"⚠️ Unused fertilizers: {', '.join(unused)}")
                details = inv_check.get("details", {})
                if details:
                    for res in details if isinstance(details, list) else [details]:
                        with st.expander(f"Using {res['Source']}", expanded=True):
                            for line in res["Prescription"]:
                                st.info(line)
                            st.metric("Total Weight", f"{res['Total Weight']:.2f} kg")
            else:
                # inv_check is invalid — surface the reason clearly
                st.warning(f"⚠️ **Status: Insufficient.** {inv_check['reason']}")

                # Granular per-nutrient tips from inventory_sufficiency
                missing = inv_suff.get("missing_nutrients", [])
                if "Nitrogen (N)" in missing:
                    st.caption("💡 *Tip: Consider adding Urea (46-0-0) or Ammonium Sulfate.*")
                if "Phosphorus (P)" in missing:
                    st.caption("💡 *Tip: Consider adding Single Superphosphate 16-20-0.*")
                if "Potassium (K)" in missing:
                    st.caption("💡 *Tip: Consider adding Muriate of Potash (0-0-60).*")

                # If solve_npk still produced a partial result, show it for reference
                partial = inv_check.get("details")
                if partial and partial.get("candidate_prescription"):
                    with st.expander("🔍 Partial Mix (for reference)", expanded=False):
                        for line in partial["candidate_prescription"]:
                            st.info(line)
                        applied = partial.get("applied", {})
                        p_col1, p_col2, p_col3 = st.columns(3)
                        p_col1.metric("Applied N", f"{applied.get('N', 0):.2f} kg")
                        p_col2.metric("Applied P", f"{applied.get('P', 0):.2f} kg")
                        p_col3.metric("Applied K", f"{applied.get('K', 0):.2f} kg")

            st.divider()

            # ── 2. CALCULATED REQUIREMENTS ───────────────────────────────────
            st.subheader("2. Calculated Requirements for your Land")

            summary_df = pd.DataFrame(
                [
                    {
                        "Analysis Step": "Requirement for your Land",
                        "N (kg)": total_base["N"],
                        "P (kg)": total_base["P"],
                        "K (kg)": total_base["K"],
                    }
                ]
            ).set_index("Analysis Step")

            st.table(summary_df.style.format("{:.2f}"))

            # ── 3. FERTILIZER APPLICATION OPTIONS ────────────────────────────
            st.subheader("3. Fertilizer Application Options")

            if standard_mix:
                for res in standard_mix:
                    with st.expander(f"Using {res['Source']}"):
                        for line in res["Prescription"]:
                            st.info(line)
                        st.metric("Total Weight", f"{res['Total Weight']:.2f} kg")
            else:
                st.warning("No standard fertilizer mixes could be generated for the current inputs.")

    except Exception as e:
        st.error(f"Configuration Error: {e}")

def main():
    run_ui()  

if __name__ == "__main__":
    run_ui()