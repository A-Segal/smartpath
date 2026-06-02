import numpy as np
from scipy.optimize import linprog
import csv
from services.batch_algoritm.options_of_Inlay_filter_by_meals import dict_of_valid_divide_options

# =========================
# CONFIG
# =========================
CSV_OUTPUT_FOLDER = "csvfiles"
CSV_FILENAME = "allocation_results.csv"
# MAX_DISTANCE = None  # לא מגבילים מרחק עכשיו

# =========================
# TRANSPORTATION ALGORITHM
# =========================
def run_transportation_lp(db):
    """
    Solve a real Transportation Problem:
    - Each recipient can receive portions from multiple centers
    - Maximizes fulfilled demand
    - Minimizes distance cost
    """
    # --- Load valid options from DB ---
    results = dict_of_valid_divide_options(db)
    if not results:
        return {"status": "NO_DATA", "allocation": []}

    # --- Create unique lists of centers and recipients ---
    center_ids = sorted({r["center_id"] for r in results})
    recipient_ids = sorted({r["recipient_id"] for r in results})

    # --- Build supply and demand vectors ---
    supply_dict = {c: sum(r["capacity"] for r in results if r["center_id"] == c) for c in center_ids}
    demand_dict = {r: sum(r["demand"] for r in results if r["recipient_id"] == r) for r in recipient_ids}

    supply = np.array([supply_dict[c] for c in center_ids])
    demand = np.array([demand_dict[r] for r in recipient_ids])

    # --- Build cost matrix ---
    cost_matrix = np.full((len(center_ids), len(recipient_ids)), 1e6)  # large number for invalid options

    # fill only valid pairs
    for r in results:
        c_idx = center_ids.index(r["center_id"])
        r_idx = recipient_ids.index(r["recipient_id"])
        # cost = distance (you can also add other factors)
        cost_matrix[c_idx, r_idx] = r["distance_km"]

    # --- Flatten the cost matrix for linprog ---
    c_vec = cost_matrix.flatten()

    # --- Build constraints for supply (<=) ---
    A_supply = np.zeros((len(center_ids), len(c_vec)))
    for i, _ in enumerate(center_ids):
        for j in range(len(recipient_ids)):
            A_supply[i, i*len(recipient_ids) + j] = 1
    b_supply = supply

    # --- Build constraints for demand (==) ---
    A_demand = np.zeros((len(recipient_ids), len(c_vec)))
    for j, _ in enumerate(recipient_ids):
        for i in range(len(center_ids)):
            A_demand[j, i*len(recipient_ids) + j] = 1
    b_demand = demand

    # --- Combine constraints ---
    A_eq = A_demand
    b_eq = b_demand
    A_ub = A_supply
    b_ub = b_supply

    # --- Solve LP ---
    result = linprog(
        c=c_vec,
        A_ub=A_ub,
        b_ub=b_ub,
        A_eq=A_eq,
        b_eq=b_eq,
        bounds=(0, None),
        method='highs'
    )

    # --- Decode allocation ---
    allocation = []
    if result.success:
        x_opt = result.x.reshape(cost_matrix.shape)
        for i, c_id in enumerate(center_ids):
            for j, r_id in enumerate(recipient_ids):
                if x_opt[i, j] > 0:
                    allocation.append({
                        "center_id": c_id,
                        "recipient_id": r_id,
                        "allocated": x_opt[i, j],
                        "recipient_demand": demand[j],
                        "center_capacity": supply[i],
                        "distance": cost_matrix[i, j]
                    })
    return {
        "status": "Optimal" if result.success else "Failed",
        "allocation": allocation,
        "unassigned": [recipient_ids[j] for j, d in enumerate(demand) if sum(result.x[i*len(recipient_ids)+j] for i in range(len(center_ids))) == 0] if result.success else []
    }


# =========================
# TEST SCRIPT
# =========================
def test_transportation_algorithm(db):
    result = run_transportation_lp(db)

    if result["status"] != "Optimal":
        print(f"Solver status: {result['status']}")
        return

    allocation = result["allocation"]
    if not allocation:
        print("No allocation returned")
        return

    # --- Print allocation ---
    print("Allocation results:")
    for a in allocation:
        print(f"Recipient {a['recipient_id']} <- Center {a['center_id']}, "
              f"Amount: {a['allocated']:.1f}, "
              f"Recipient Demand: {a['recipient_demand']}, "
              f"Center Capacity: {a['center_capacity']}, "
              f"Distance: {a['distance']:.2f} km")

    # --- Save CSV ---
    csv_path = f"{CSV_OUTPUT_FOLDER}/{CSV_FILENAME}"
    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["recipient_id","center_id","allocated","recipient_demand","center_capacity","distance"])
        writer.writeheader()
        for a in allocation:
            writer.writerow(a)

    print(f"\nCSV saved to: {csv_path}")
    print(f"Total assigned recipients: {len(set(a['recipient_id'] for a in allocation))}")
    print(f"Unassigned recipients: {len(result.get('unassigned', []))}")


# =========================
# RUN TEST
# =========================
if __name__ == "__main__":
    from db_connection import get_session
    db = get_session()
    test_transportation_algorithm(db)