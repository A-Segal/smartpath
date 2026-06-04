import pulp

from services.batch_algoritm.options_of_Inlay_filter_by_meals import (
    dict_of_valid_divide_options
)

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

MAX_DISTANCE_KM = 100

PRIORITY_WEIGHT = 100000
DISTANCE_WEIGHT = 5
CAPACITY_MATCH_WEIGHT = 1

TOP_K_CENTERS = 10


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def run_transportation_problem(db):

    results = dict_of_valid_divide_options(db)

    if not results:
        return {
            "status": "NO_DATA",
            "allocation": []
        }

    # --------------------------------------------------
    # Build Centers / Recipients
    # --------------------------------------------------

    centers = {}
    recipients = {}

    for row in results:

        center_id = int(row["center_id"])
        recipient_id = int(row["recipient_id"])

        if center_id not in centers:
            centers[center_id] = int(row["capacity"])

        if recipient_id not in recipients:
            recipients[recipient_id] = int(row["demand"])

    center_ids = sorted(centers.keys())
    recipient_ids = sorted(recipients.keys())

    # --------------------------------------------------
    # Build valid pairs
    # --------------------------------------------------

    recipient_options = {}

    for row in results:

        c = int(row["center_id"])
        r = int(row["recipient_id"])

        distance = float(row["distance_km"])

        if distance > MAX_DISTANCE_KM:
            continue

        recipient_options.setdefault(r, []).append(
            (c, distance)
        )

    # --------------------------------------------------
    # Keep only TOP K closest centers
    # --------------------------------------------------

    pairs = set()
    distance_map = {}

    for recipient_id, options in recipient_options.items():

        options.sort(key=lambda x: x[1])

        for center_id, distance in options[:TOP_K_CENTERS]:

            pairs.add((center_id, recipient_id))
            distance_map[(center_id, recipient_id)] = distance

    if not pairs:
        return {
            "status": "NO_VALID_PAIRS",
            "allocation": []
        }

    # --------------------------------------------------
    # MILP MODEL
    # --------------------------------------------------

    model = pulp.LpProblem(
        "Modified_Transportation_Problem",
        pulp.LpMaximize
    )

    # Assignment variable

    x = pulp.LpVariable.dicts(
        "assign",
        pairs,
        cat="Binary"
    )

    # Recipient served variable

    served = pulp.LpVariable.dicts(
        "served",
        recipient_ids,
        cat="Binary"
    )

    # --------------------------------------------------
    # Objective
    # --------------------------------------------------

    objective_terms = []

    # Maximize served recipients
    objective_terms.append(
        PRIORITY_WEIGHT *
        pulp.lpSum(
            served[r]
            for r in recipient_ids
        )
    )

    # Distance score
    objective_terms.append(
        -DISTANCE_WEIGHT *
        pulp.lpSum(
            distance_map[(c, r)] * x[(c, r)]
            for (c, r) in pairs
        )
    )

    # Capacity match score
    capacity_match_terms = []

    for (c, r) in pairs:

        remaining_capacity = (
            centers[c] - recipients[r]
        )

        utilization_score = (
            recipients[r] / centers[c]
        )

        capacity_match_terms.append(
            utilization_score * x[(c, r)]
        )

    objective_terms.append(
        CAPACITY_MATCH_WEIGHT *
        pulp.lpSum(capacity_match_terms)
    )

    model += pulp.lpSum(objective_terms)

    # --------------------------------------------------
    # Recipient constraints
    # --------------------------------------------------

    for r in recipient_ids:

        assignments = pulp.lpSum(
            x[(c, r)]
            for c in center_ids
            if (c, r) in x
        )

        model += assignments <= 1

        model += served[r] == assignments

    # --------------------------------------------------
    # Center capacity constraints
    # --------------------------------------------------

    for c in center_ids:

        model += (

            pulp.lpSum(

                recipients[r] * x[(c, r)]

                for r in recipient_ids
                if (c, r) in x

            )

            <= centers[c]

        )

    # --------------------------------------------------
    # Solve
    # --------------------------------------------------

    solver = pulp.PULP_CBC_CMD(
        msg=False
    )

    model.solve(solver)

    # --------------------------------------------------
    # Build allocation
    # --------------------------------------------------

    allocation = []

    for (c, r), var in x.items():

        if pulp.value(var) == 1:

            allocation.append({

                "center_id": c,
                "recipient_id": r,

                "demand": recipients[r],

                "capacity": centers[c],

                "remaining_capacity_after_assignment":
                    centers[c] - recipients[r],

                "distance": round(
                    distance_map[(c, r)],
                    3
                )

            })

    assigned_recipients = {
        row["recipient_id"]
        for row in allocation
    }

    unassigned = [
        r
        for r in recipient_ids
        if r not in assigned_recipients
    ]

    return {

        "status":
            pulp.LpStatus[model.status],

        "assigned_count":
            len(assigned_recipients),

        "unassigned_count":
            len(unassigned),

        "allocation":
            allocation,

        "unassigned":
            unassigned
    }