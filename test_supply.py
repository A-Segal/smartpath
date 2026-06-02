import csv
from services.batch_algoritm.try_tranportation_algoritm import run_transportation_problem

# ------------------------
# CONFIG
# ------------------------
CSV_OUTPUT_FOLDER = "csvfiles"
CSV_FILENAME = "allocation_results.csv"

# ------------------------
# TEST FUNCTION
# ------------------------
def test_transportation_algorithm(db):
    """
    Test the transportation algorithm:
    - Run the algorithm
    - Print the results
    - Save CSV with recipient, center, amount assigned, demand, center capacity, distance
    """

    # --- Run the algorithm ---
    result = run_transportation_problem(db)

    # --- Check if there is a solution ---
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
        print(
            f"Recipient {a['recipient_id']} <- Center {a['center_id']}, "
            f"Amount: {a['amount']}, Recipient Demand: {a['recipient_demand']}, "
            f"Center Capacity: {a['center_capacity']}, Distance: {a['distance']:.2f} km"
        )

    # --- Save CSV ---
    csv_path = f"{CSV_OUTPUT_FOLDER}/{CSV_FILENAME}"
    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "recipient_id",
                "center_id",
                "amount",
                "recipient_demand",
                "center_capacity",
                "distance"
            ]
        )
        writer.writeheader()
        for a in allocation:
            writer.writerow({
                "recipient_id": a["recipient_id"],
                "center_id": a["center_id"],
                "amount": a["amount"],
                "recipient_demand": a["recipient_demand"],
                "center_capacity": a["center_capacity"],
                "distance": a["distance"]
            })

    print(f"\nCSV saved to: {csv_path}")
    print(f"Total assigned recipients: {len(allocation)}")
    print(f"Unassigned recipients: {len(result.get('unassigned', []))}")


# ------------------------
# RUN TEST
# ------------------------
if __name__ == "__main__":
    from db_connection import get_session  # פונקציה שמחזירה session SQLAlchemy
    db = get_session()
    test_transportation_algorithm(db)