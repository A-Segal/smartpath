#הפונקציה מחזירה מילון של כל האפשרויות
#של השיבוץ החלוקה
#מוקד-מוטב-מרחק ב ק"מ
# בלי שום סינון




from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from models.recipient import Recipient
from models.distribution_center import DistributionCenter
from models.recipient_request import RecipientRequest
from models.DS_request import DS_Request
from services.googleMaps import distance_between_points

def dict_of_all_options_divides(db: Session):
    today = date.today()

    start_of_day = datetime.combine(today, datetime.min.time())
    end_of_day = datetime.combine(today, datetime.max.time())

    # Bulk fetch (NO N+1 QUERIES)
    ds_requests = db.query(DS_Request).filter(
        DS_Request.request_date.between(start_of_day, end_of_day)
    ).all()

    recipient_requests = db.query(RecipientRequest).filter(
        RecipientRequest.request_date.between(start_of_day, end_of_day)
    ).all()

    centers = {c.id: c for c in db.query(DistributionCenter).all()}
    recipients = {r.id: r for r in db.query(Recipient).all()}

    results = []

    # Main computation
    for ds in ds_requests:
        center = centers.get(ds.DistributionCenterID)
        if not center:
            continue

        c_lat = float(center.location_lat)
        c_lng = float(center.location_lng)

        for rr in recipient_requests:
            recipient = recipients.get(rr.RecipientID)
            if not recipient or recipient.location_lat is None or recipient.location_lng is None:
                continue

            distance = distance_between_points(
                c_lat,
                c_lng,
                float(recipient.location_lat),
                float(recipient.location_lng)
            )

            results.append({
                "distribution_center_id": center.id,
                "recipient_id": recipient.id,
                "distance_km": distance
            })

    return results