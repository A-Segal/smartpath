
import csv
from db_connection import get_session
from services.calc_all_options_of_distances_disCenter_and_rec import calc_all_options_of_distances_between_distrCenter_and_recipients

def try_the_first():
    with get_session() as db:
        distances = calc_all_options_of_distances_between_distrCenter_and_recipients(db)

        # הדפסה של תוצאות
        if distances:
            for item in distances:
                print(f"distrCenter: {item['distrCenter']} -> recipient_id: {item['recipient_id']} | dist: {item['distance_km']:.2f} ")
        else:
            print("אין בקשות להיום.")


if __name__ == "__main__":
    try_the_first()