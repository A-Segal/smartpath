from models.vehicle import Vehicle


from sqlalchemy.orm import Session

class VehicleRepository:
    def __init__(self, session: Session):
        self.session = session

    def add_vehicle(self, volunteer_id: int, capacity: int) -> Vehicle:
        vehicle = Vehicle(VolunteerID=volunteer_id, capacity=capacity)
        self.session.add(vehicle)
        self.session.commit()
        self.session.refresh(vehicle)
        return vehicle

    def get_vehicle_by_id(self, vehicle_id: int) -> Vehicle:
        return self.session.query(Vehicle).filter(Vehicle.id == vehicle_id).first()

    def get_vehicles_by_volunteer(self, volunteer_id: int):
        return self.session.query(Vehicle).filter(Vehicle.VolunteerID == volunteer_id).all()

    def update_vehicle(self, vehicle_id: int, volunteer_id: int = None, capacity: int = None) -> Vehicle:
        vehicle = self.get_vehicle_by_id(vehicle_id)
        if vehicle is None:
            return None
        if volunteer_id is not None:
            vehicle.VolunteerID = volunteer_id
        if capacity is not None:
            vehicle.capacity = capacity
        self.session.commit()
        self.session.refresh(vehicle)
        return vehicle

    def delete_vehicle(self, vehicle_id: int) -> bool:
        vehicle = self.get_vehicle_by_id(vehicle_id)
        if vehicle is None:
            return False
        self.session.delete(vehicle)
        self.session.commit()
        return True

    def get_all_vehicles(self):
        return self.session.query(Vehicle).all()