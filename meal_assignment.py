# """
# meal_assignment.py
# ------------------
# שיבוץ ארוחות ממוקדי חלוקה ליעדים.
#
# אלגוריתם: Greedy + Capacitated Assignment
# """
#
# import math
# from dataclasses import dataclass, field
# from typing import Optional
#
#
# # ---------------------------------------------------------------------------
# # מודלים
# # ---------------------------------------------------------------------------
#
# @dataclass
# class DistributionHub:
#     """מוקד חלוקה"""
#     id: str
#     lat: float
#     lon: float
#     max_portions: int
#     available_portions: int = field(init=False)
#
#     def __post_init__(self):
#         self.available_portions = self.max_portions
#
#
# @dataclass
# class Destination:
#     """יעד"""
#     id: str
#     lat: float
#     lon: float
#     required_portions: int
#     assigned_portions: int = 0
#     assigned_hub_id: Optional[str] = None
#
#
# @dataclass
# class Assignment:
#     """תוצאת שיבוץ בודד"""
#     hub_id: str
#     destination_id: str
#     portions: int
#     distance_km: float
#
#
# # ---------------------------------------------------------------------------
# # פונקציות עזר
# # ---------------------------------------------------------------------------
#
# def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
#     """מרחק בק\"מ בין שתי נקודות GPS (Haversine formula)"""
#     R = 6371
#     dlat = math.radians(lat2 - lat1)
#     dlon = math.radians(lon2 - lon1)
#     a = (
#         math.sin(dlat / 2) ** 2
#         + math.cos(math.radians(lat1))
#         * math.cos(math.radians(lat2))
#         * math.sin(dlon / 2) ** 2
#     )
#     return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
#
#
# def build_distance_matrix(
#     hubs: list[DistributionHub],
#     destinations: list[Destination],
# ) -> dict[tuple[str, str], float]:
#     """בונה מטריצת מרחקים מוקד → יעד"""
#     return {
#         (hub.id, dest.id): haversine_distance(hub.lat, hub.lon, dest.lat, dest.lon)
#         for hub in hubs
#         for dest in destinations
#     }
#
#
# # ---------------------------------------------------------------------------
# # אלגוריתם שיבוץ ראשי
# # ---------------------------------------------------------------------------
#
# def assign_meals(
#     hubs: list[DistributionHub],
#     destinations: list[Destination],
#     max_distance_km: float = 50.0,
# ) -> tuple[list[Assignment], dict]:
#     """
#     שיבוץ ארוחות ממוקדי חלוקה ליעדים.
#
#     אסטרטגיה (Greedy + Capacitated):
#       1. מיין יעדים לפי דרישה יורדת (הדחוף קודם).
#       2. לכל יעד – בחר את המוקד הקרוב ביותר עם מלאי פנוי.
#       3. הקצה כמה שיותר מנות מאותו מוקד (עד מלאי / דרישה).
#       4. אם נשאר מחסור – חפש מוקד קרוב נוסף.
#
#     פרמטרים:
#       hubs            – רשימת מוקדי חלוקה
#       destinations    – רשימת יעדים
#       max_distance_km – מרחק מקסימלי מותר בק"מ
#
#     מחזיר:
#       (assignments, stats)
#       assignments – רשימת Assignment
#       stats       – dict עם ניצול, כיסוי ומרחק ממוצע
#     """
#     dist_matrix = build_distance_matrix(hubs, destinations)
#     assignments: list[Assignment] = []
#
#     sorted_destinations = sorted(
#         destinations, key=lambda d: d.required_portions, reverse=True
#     )
#
#     for dest in sorted_destinations:
#         remaining_need = dest.required_portions - dest.assigned_portions
#
#         eligible_hubs = [
#             h for h in hubs
#             if h.available_portions > 0
#             and dist_matrix[(h.id, dest.id)] <= max_distance_km
#         ]
#         eligible_hubs.sort(key=lambda h: dist_matrix[(h.id, dest.id)])
#
#         for hub in eligible_hubs:
#             if remaining_need <= 0:
#                 break
#
#             portions_to_assign = min(hub.available_portions, remaining_need)
#             distance = dist_matrix[(hub.id, dest.id)]
#
#             assignments.append(Assignment(
#                 hub_id=hub.id,
#                 destination_id=dest.id,
#                 portions=portions_to_assign,
#                 distance_km=round(distance, 2),
#             ))
#
#             hub.available_portions -= portions_to_assign
#             dest.assigned_portions += portions_to_assign
#             remaining_need -= portions_to_assign
#
#     # סטטיסטיקות
#     total_required = sum(d.required_portions for d in destinations)
#     total_assigned = sum(d.assigned_portions for d in destinations)
#     total_available = sum(h.max_portions for h in hubs)
#     total_used = total_available - sum(h.available_portions for h in hubs)
#
#     stats = {
#         "coverage_pct": round(100 * total_assigned / total_required, 1) if total_required else 0,
#         "utilization_pct": round(100 * total_used / total_available, 1) if total_available else 0,
#         "avg_distance_km": round(
#             sum(a.distance_km * a.portions for a in assignments)
#             / sum(a.portions for a in assignments),
#             2,
#         ) if assignments else 0,
#         "unmet_destinations": [
#             d.id for d in destinations if d.assigned_portions < d.required_portions
#         ],
#     }
#
#     return assignments, stats
#
#
# # ---------------------------------------------------------------------------
# # הכנת משימות למתנדבים
# # ---------------------------------------------------------------------------
#
# def prepare_volunteer_tasks(assignments: list[Assignment]) -> list[dict]:
#     """
#     ממיר שיבוץ ארוחות למשימות למתנדבים.
#     כל Assignment = משימת שינוע אחת.
#     """
#     return [
#         {
#             "task_id": f"TASK-{i + 1:03d}",
#             "hub_id": a.hub_id,
#             "destination_id": a.destination_id,
#             "portions": a.portions,
#             "distance_km": a.distance_km,
#             "status": "pending",
#         }
#         for i, a in enumerate(assignments)
#     ]
#
#
# # ---------------------------------------------------------------------------
# # גרסת LP אופציונלית (דורשת: pip install scipy numpy)
# # ---------------------------------------------------------------------------
#
# def assign_meals_lp(hubs: list[DistributionHub], destinations: list[Destination]):
#     """
#     שיבוץ אופטימלי מלא באמצעות Linear Programming.
#     משתמש ב-scipy.optimize.linprog (solver: HiGHS).
#     מתאים כאשר דרוש פתרון גלובלי מדויק.
#     """
#     try:
#         from scipy.optimize import linprog
#         import numpy as np
#     except ImportError:
#         raise ImportError("התקן את הספריות: pip install scipy numpy")
#
#     n, m = len(hubs), len(destinations)
#     dist = np.array([
#         [haversine_distance(h.lat, h.lon, d.lat, d.lon) for d in destinations]
#         for h in hubs
#     ]).flatten()
#
#     # אילוצי קיבולת מוקדים (≤)
#     A_ub, b_ub = [], []
#     for i, hub in enumerate(hubs):
#         row = [0] * (n * m)
#         for j in range(m):
#             row[i * m + j] = 1
#         A_ub.append(row)
#         b_ub.append(hub.max_portions)
#
#     # אילוצי דרישת יעדים (=)
#     A_eq, b_eq = [], []
#     for j, dest in enumerate(destinations):
#         row = [0] * (n * m)
#         for i in range(n):
#             row[i * m + j] = 1
#         A_eq.append(row)
#         b_eq.append(dest.required_portions)
#
#     result = linprog(
#         dist,
#         A_ub=A_ub, b_ub=b_ub,
#         A_eq=A_eq, b_eq=b_eq,
#         bounds=[(0, None)] * (n * m),
#         method="highs",
#     )
#     return result
#
#
# # ---------------------------------------------------------------------------
# # דוגמת שימוש
# # ---------------------------------------------------------------------------
#
# if __name__ == "__main__":
#     hubs = [
#         DistributionHub("HUB-1", lat=32.08, lon=34.78, max_portions=50),
#         DistributionHub("HUB-2", lat=32.10, lon=34.80, max_portions=30),
#     ]
#     destinations = [
#         Destination("DEST-A", lat=32.09, lon=34.79, required_portions=40),
#         Destination("DEST-B", lat=32.12, lon=34.82, required_portions=25),
#         Destination("DEST-C", lat=32.07, lon=34.77, required_portions=10),
#     ]
#
#     assignments, stats = assign_meals(hubs, destinations, max_distance_km=30)
#     volunteer_tasks = prepare_volunteer_tasks(assignments)
#
#     print("=== שיבוץ ===")
#     for a in assignments:
#         print(f"  {a.hub_id} → {a.destination_id}: {a.portions} מנות | {a.distance_km} ק\"מ")
#
#     print("\n=== סטטיסטיקות ===")
#     for k, v in stats.items():
#         print(f"  {k}: {v}")
#
#     print("\n=== משימות מתנדבים ===")
#     for t in volunteer_tasks:
#         print(f"  {t['task_id']}: {t['hub_id']} → {t['destination_id']} ({t['portions']} מנות)")
