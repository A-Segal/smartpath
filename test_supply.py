import os
import csv

from services.batch_algoritm.transportation_algoritm import (
    run_transportation_problem
)


def test_transportation_algorithm(db):
    """
    מריץ את האלגוריתם,
    מדפיס תוצאות,
    ותמיד יוצר CSV בתוך csvfiles.
    """

    print("\n===================================")
    print("Transportation Problem Test")
    print("===================================\n")

    # ---------------------------------
    # Run algorithm
    # ---------------------------------

    result = run_transportation_problem(db)

    status = result.get("status", "UNKNOWN")

    print(f"Solver Status: {status}")

    allocation = result.get("allocation", [])

    print(f"Assignments Found: {len(allocation)}")

    # ---------------------------------
    # Print allocation
    # ---------------------------------

    if allocation:

        print("\nAssignments:\n")

        for row in allocation:

            print(
                f"Center {row['center_id']} -> "
                f"Recipient {row['recipient_id']} | "
                f"Demand={row['demand']} | "
                f"Capacity={row['capacity']} | "
                f"Distance={row['distance']:.2f} km"
            )

    else:

        print("\nNo allocation returned.\n")

    # ---------------------------------
    # Create csv folder
    # ---------------------------------

    os.makedirs("csvfiles", exist_ok=True)

    csv_path = os.path.join(
        "csvfiles",
        "transportation_results2.csv"
    )

    # ---------------------------------
    # Create CSV
    # ---------------------------------

    with open(
        csv_path,
        mode="w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "center_id",
            "recipient_id",
            "demand",
            "capacity",
            "distance_km"
        ])

        for row in allocation:

            writer.writerow([
                row.get("center_id"),
                row.get("recipient_id"),
                row.get("demand"),
                row.get("capacity"),
                row.get("distance")
            ])

    print(f"\nCSV created: {csv_path}")

    # ---------------------------------
    # Summary
    # ---------------------------------

    print("\nSummary:")
    print(
        "Assigned Recipients:",
        result.get("assigned_count", len(allocation))
    )

    print(
        "Unassigned Recipients:",
        result.get("unassigned_count", 0)
    )

    if result.get("unassigned"):

        print("\nUnassigned Recipient IDs:")

        for recipient_id in result["unassigned"]:
            print(recipient_id)


# ---------------------------------
# RUN TEST
# ---------------------------------

if __name__ == "__main__":

    from db_connection import get_session

    db = get_session()

    try:

        test_transportation_algorithm(db)

    finally:

        db.close()