from flask import Blueprint, request, jsonify
from repository.VolunteerRepository import VolunteerRepository
from db_connection import SessionLocal

# Blueprint עבור Volunteers
volunteer_bp = Blueprint('volunteer_bp', __name__, url_prefix='/volunteers')

@volunteer_bp.route('', methods=['POST'])
def add_volunteer():
    db_session = SessionLocal()
    try:
        volunteer_repo = VolunteerRepository(db_session)
        data = request.get_json()
        new_volunteer = volunteer_repo.create_volunteer(
            fname=data['fname'],
            lname=data['lname'],
            username=data['username'],
            password=data['password'],
            vehicle_capacity=data['vehicle_capacity'],
            mail=data.get('mail'),
            phone=data.get('phone')
        )
        return jsonify({
            'id': new_volunteer.id,
            'fname': new_volunteer.fname,
            'lname': new_volunteer.lname,
            'username': new_volunteer.username
        }), 201
    finally:
        db_session.close()

@volunteer_bp.route('/<int:volunteer_id>', methods=['GET'])
def get_volunteer(volunteer_id):
    db_session = SessionLocal()
    try:
        volunteer_repo = VolunteerRepository(db_session)
        volunteer = volunteer_repo.get_volunteer(volunteer_id)
        if volunteer is None:
            return jsonify({'error': 'Volunteer not found'}), 404
        return jsonify({
            'id': volunteer.id,
            'fname': volunteer.fname,
            'lname': volunteer.lname,
            'username': volunteer.username
        })
    finally:
        db_session.close()