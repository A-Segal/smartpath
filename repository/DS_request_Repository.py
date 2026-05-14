from sqlalchemy.orm import Session
from models.DS_request import DS_Request
from datetime import datetime

class DSRequestRepository:
    def __init__(self, db: Session):
        self.db = db

    # יצירת בקשה חדשה
    def create_request(self, distribution_center_id: int, amount_of_meals: int, request_date: datetime = None) -> DS_Request:
        if request_date is None:
            request_date = datetime.now()
        new_request = DS_Request(
            DistributionCenterID=distribution_center_id,
            amount_of_meals=amount_of_meals,
            request_date=request_date
        )
        self.db.add(new_request)
        self.db.commit()
        self.db.refresh(new_request)
        return new_request

    # קבלת בקשה לפי ID
    def get_request(self, request_id: int) -> DS_Request | None:
        return self.db.query(DS_Request).filter(DS_Request.id == request_id).first()

    # קבלת כל הבקשות
    def get_all_requests(self) -> list[DS_Request]:
        return self.db.query(DS_Request).all()

    # עדכון בקשה
    def update_request(self, request_id: int, amount_of_meals: int = None, request_date: datetime = None) -> DS_Request | None:
        request = self.get_request(request_id)
        if request:
            if amount_of_meals is not None:
                request.amount_of_meals = amount_of_meals
            if request_date is not None:
                request.request_date = request_date
            self.db.commit()
            self.db.refresh(request)
        return request

    # מחיקת בקשה
    def delete_request(self, request_id: int) -> bool:
        request = self.get_request(request_id)
        if request:
            self.db.delete(request)
            self.db.commit()
            return True
        return False