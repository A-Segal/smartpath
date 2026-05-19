#שולפת ומחזירה את כל הבקשות והארוחות של היום למקבלים ולמרכזי ההפצה, מחשבת את המרחקים בין
# כל מרכז לכל מקבל, ומחזירה dictionary של כל האפשרויות,
# בלי סינון של האפשרויות הלא רלוונטיות ,לפי כמות המנות.


from ctypes import cast
from sqlalchemy.orm import Session
from models.recipient import Recipient
from models.distribution_center import DistributionCenter
from models.recipient_request import RecipientRequest
from models.DS_request import DS_Request
from services.googleMaps import distance_between_points
from sqlalchemy import cast, Date, func
from datetime import date


def calc_all_options_of_distances_between_distrCenter_and_recipients(db: Session):
    today = date.today()
    ds_requests_today = db.query(DS_Request).filter(
        cast(DS_Request.request_date, Date) == today
    ).all()

    recipient_requests_today = db.query(RecipientRequest).filter(
        cast(RecipientRequest.request_date, Date) == today
    ).all()
    results = []

    for ds_req in ds_requests_today:
        distrCenter = db.query(DistributionCenter).filter(
            DistributionCenter.id == ds_req.DistributionCenterID
        ).first()

        for rec_req in recipient_requests_today:
            rec = db.query(Recipient).filter(
                Recipient.id == rec_req.RecipientID
            ).first()

            distance_km = distance_between_points(
                float(distrCenter.location_lat),
                float(distrCenter.location_lng),
                float(rec.location_lat),
                float(rec.location_lng)
            )

            results.append({
                "distrCenter": distrCenter.id,
                "recipient_id": rec.id,
                "distance_km": distance_km
            })

    return results
