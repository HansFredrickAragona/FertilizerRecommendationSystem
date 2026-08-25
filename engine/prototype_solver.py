def solve_npk_with_inv(t_n, t_p, t_k, inventory, selected_inventory, rules, area, unit_label):
    """Generate fertilizer mix options based on target nutrient requirements.

    This implementation generates prescription combinations from the project
    inventory and filters results to include at least one selected inventory item
    when selected inventory is provided.

    Args:
        t_n: Total nitrogen requirement for the field.
        t_p: Total phosphorus requirement for the field.
        t_k: Total potassium requirement for the field.
        inventory: Loaded fertilizer inventory list.
        selected_inventory: List of already selected fertilizers.
        rules: Engine rule definitions including constraints and output formatting.
        area: The raw area value entered by the user.
        unit_label: The unit string used for display in prescriptions.

    Returns:
        list: Sorted fertilizer combination results limited by rule constraints.
    """
    results = []
    max_target = max(t_n, t_p, t_k)
    if max_target <= 0:
        return []

    precision = 3 if max_target < 1.0 else rules["constraints"]["precision_decimals"]
    allow_over = rules["constraints"]["allow_over_fertilization"]
    sack_size = rules["constraints"].get("sack_size_kg", 50)

    p_sources = [f for f in inventory if f["p"] > 0]
    n_fillers = [f for f in inventory if f["n"] > 0 and f["p"] == 0 and f["k"] == 0]
    k_fillers = [f for f in inventory if f["k"] > 0 and f["n"] == 0 and f["p"] == 0]

    selected_names = {f["name"] for f in selected_inventory}
    require_selected = bool(selected_names)
    seen_combinations = set()

    for p_fert in p_sources:
        for n_filler in [None] + n_fillers:
            for k_filler in [None] + k_fillers:
                if n_filler is None and k_filler is None and t_p <= 0:
                    continue

                qty_p = (t_p / p_fert["p"]) * 100 if p_fert["p"] > 0 else 0
                n_provided = (qty_p * p_fert["n"]) / 100
                p_provided = (qty_p * p_fert["p"]) / 100
                k_provided = (qty_p * p_fert["k"]) / 100

                rem_n = t_n - n_provided
                rem_k = t_k - k_provided

                if not allow_over and (rem_n < -0.01 or rem_k < -0.01):
                    continue

                if rem_n > 0.01 and n_filler is None:
                    continue
                if rem_k > 0.01 and k_filler is None:
                    continue

                qty_n = (max(0, rem_n) / n_filler["n"]) * 100 if rem_n > 0.01 and n_filler else 0
                qty_k = (max(0, rem_k) / k_filler["k"]) * 100 if rem_k > 0.01 and k_filler else 0

                if qty_n <= 0 and qty_p <= 0 and qty_k <= 0:
                    continue

                used_items = []
                if qty_n > 0 and n_filler is not None:
                    used_items.append(n_filler)
                if qty_p > 0:
                    used_items.append(p_fert)
                if qty_k > 0 and k_filler is not None:
                    used_items.append(k_filler)

                if require_selected:
                    if not any(item["name"] in selected_names for item in used_items):
                        continue

                source_names = tuple(item["name"] for item in used_items)
                if source_names in seen_combinations:
                    continue
                seen_combinations.add(source_names)

                total_n = n_provided + ((qty_n * n_filler["n"]) / 100 if n_filler else 0)
                total_k = k_provided + ((qty_k * k_filler["k"]) / 100 if k_filler else 0)

                fmt = rules["output_format"]
                prescription = []
                if qty_n > 0:
                    prescription.append(
                        fmt.format(
                            qty=round(qty_n, precision),
                            sacks=round(qty_n / sack_size, precision),
                            area=area,
                            unit=unit_label,
                            fertilizer_name=n_filler["name"],
                        )
                    )
                if qty_p > 0:
                    prescription.append(
                        fmt.format(
                            qty=round(qty_p, precision),
                            sacks=round(qty_p / sack_size, precision),
                            area=area,
                            unit=unit_label,
                            fertilizer_name=p_fert["name"],
                        )
                    )
                if qty_k > 0:
                    prescription.append(
                        fmt.format(
                            qty=round(qty_k, precision),
                            sacks=round(qty_k / sack_size, precision),
                            area=area,
                            unit=unit_label,
                            fertilizer_name=k_filler["name"],
                        )
                    )

                results.append(
                    {
                        "Source": " + ".join(source_names),
                        "Prescription": prescription,
                        "Total Weight": qty_n + qty_p + qty_k,
                        "Total Sacks": sum(
                            round(qty / sack_size, precision) for qty in [qty_n, qty_p, qty_k]
                        ),
                        "Applied N": total_n,
                        "Applied P": p_provided,
                        "Applied K": total_k,
                    }
                )

    max_combos = rules["constraints"]["max_combinations"]
    return sorted(results, key=lambda x: x["Total Weight"])[:max_combos]
