import pulp
from services.batch_algoritm.options_of_Inlay_filter_by_meals import dict_of_valid_divide_options

def run_transportation_problem(db):
    results = dict_of_valid_divide_options(db)

    if not results:
        return {"status": "NO_DATA", "allocation": []}

    # -----------------------------
    # Build unique centers and recipients
    # -----------------------------
    centers = {}
    recipients = {}

    for row in results:
        center_id = int(row["center_id"])
        recipient_id = int(row["recipient_id"])

        # Only set once to avoid overwriting
        if center_id not in centers:
            centers[center_id] = int(row["capacity"])
        if recipient_id not in recipients:
            recipients[recipient_id] = int(row["demand"])

    center_ids = sorted(centers.keys())
    recipient_ids = sorted(recipients.keys())

    # -----------------------------
    # Valid pairs and distances
    # -----------------------------
    pairs = set()
    distance_map = {}
    for row in results:
        c = int(row["center_id"])
        r = int(row["recipient_id"])
        pairs.add((c, r))
        distance_map[(c, r)] = float(row["distance_km"])

    # -----------------------------
    # MILP model
    # -----------------------------
    model = pulp.LpProblem("SmartPath_Assignment", pulp.LpMaximize)

    # Binary variable: assign recipient r to center c
    x = pulp.LpVariable.dicts("assign", pairs, cat="Binary")

    # Weights for scoring
    PRIORITY_WEIGHT = 100000
    DISTANCE_WEIGHT = 1
    GAP_WEIGHT = 0.2
    DEMAND_WEIGHT = 5

    # -----------------------------
    # Objective: maximize priority, minimize distance, match demand-capacity
    # -----------------------------
    model += pulp.lpSum(
        x[(c, r)] * (
            PRIORITY_WEIGHT
            - distance_map[(c, r)] * DISTANCE_WEIGHT
            - abs(centers[c] - recipients[r]) * GAP_WEIGHT
            + recipients[r] * DEMAND_WEIGHT
        )
        for c, r in pairs
    )

    # -----------------------------
    # Constraints
    # -----------------------------

    # Each recipient can be assigned to only one center
    for r in recipient_ids:
        model += pulp.lpSum(
            x[(c, r)] for c in center_ids if (c, r) in x
        ) <= 1

    # Each center cannot exceed its capacity
    for c in center_ids:
        model += pulp.lpSum(
            recipients[r] * x[(c, r)] for r in recipient_ids if (c, r) in x
        ) <= centers[c]

    # -----------------------------
    # Solve the model
    # -----------------------------
    solver = pulp.PULP_CBC_CMD(msg=False)
    model.solve(solver)

    # -----------------------------
    # Build allocation results
    # -----------------------------
    allocation = []
    for (c, r), var in x.items():
        if pulp.value(var) == 1:
            allocation.append({
                "center_id": c,
                "recipient_id": r,
                "demand": recipients[r],
                "capacity": centers[c],
                "distance": distance_map[(c, r)]
            })

    return {
        "status": pulp.LpStatus[model.status],
        "allocation": allocation
    }