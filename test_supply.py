# -----------------------------
# קוד בדיקה להרצת האלגוריתם המעודכן
# -----------------------------
from services.batch_algoritm.tranportation_algoritm import run_transportation_problem
import csv

def test_transportation_algorithm(db):
    """
    מריץ את האלגוריתם של שיבוץ נזקקים למוקדים,
    מדפיס את התוצאה ל-console ויוצר קובץ CSV.
    """

    # קריאה לפונקציה הראשית של האלגוריתם
    result = run_transportation_problem(db)

    # בדיקה אם נמצא פתרון אופטימלי
    if result["status"] != "Optimal":
        print("לא נמצא פתרון אופטימלי. סטטוס:", result["status"])
        return

    allocation = result["allocation"]

    # הדפסת השיבוץ בקונסול
    print("שיבוץ אופטימלי:")
    for a in allocation:
        print(
            f"Recipient {a['recipient_id']} <- Center {a['center_id']}, "
            f"Demand: {a['demand']}, Center Capacity: {a['capacity']}, Distance: {a['distance']:.2f} km"
        )

    # כתיבת CSV
    csv_filename = "allocation_test_updated.csv"
    with open(csv_filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["center_id", "recipient_id", "demand", "capacity", "distance"]
        )
        writer.writeheader()
        for a in allocation:
            writer.writerow(a)

    print(f"CSV נוצר בהצלחה בשם: {csv_filename}")


# -----------------------------
# דוגמה להרצה
# -----------------------------
if __name__ == "__main__":
    from db_connection import get_session  # הכנס את הפונקציה שלך ל־DB
    db = get_session()                     # יצירת session מוכן
    test_transportation_algorithm(db)