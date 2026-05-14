from flask import Blueprint, request, jsonify
from repository.DS_request_Repository import DSRequestRepository
from db_connection import SessionLocal
from datetime import datetime

# Blueprint עבור DS_Request
ds_request_bp = Blueprint('ds_request_bp', __name__, url_prefix='/ds_request')

# יצירת בקשה חדשה (POST)
@ds_request_bp.route('', methods=['POST'])
def add_request():
    db_session = SessionLocal()
    try:
        repo = DSRequestRepository(db_session)
        data = request.get_json()

        # יצירת בקשה חדשה
        new_request = repo.create_request(
            distribution_center_id=data['DistributionCenterID'],
            amount_of_meals=data['amount_of_meals'],
            request_date=datetime.fromisoformat(data['request_date']) if data.get('request_date') else None
        )

        return jsonify({
            'id': new_request.id,
            'DistributionCenterID': new_request.DistributionCenterID,
            'amount_of_meals': new_request.amount_of_meals,
            'request_date': new_request.request_date.isoformat()
        }), 201

    finally:
        db_session.close()


# קבלת בקשה לפי ID
@ds_request_bp.route('/<int:request_id>', methods=['GET'])
def get_request(request_id):
    db_session = SessionLocal()
    try:
        repo = DSRequestRepository(db_session)
        request_obj = repo.get_request(request_id)
        if request_obj is None:
            return jsonify({'error': 'DS_Request not found'}), 404
        return jsonify({
            'id': request_obj.id,
            'DistributionCenterID': request_obj.DistributionCenterID,
            'amount_of_meals': request_obj.amount_of_meals,
            'request_date': request_obj.request_date.isoformat()
        })
    finally:
        db_session.close()

# עדכון בקשה (PUT)
@ds_request_bp.route('/<int:request_id>', methods=['PUT'])
def update_request(request_id):
    db_session = SessionLocal()
    try:
        repo = DSRequestRepository(db_session)
        data = request.get_json()

        updated_request = repo.update_request(
            request_id,
            amount_of_meals=data.get('amount_of_meals'),
            request_date=datetime.fromisoformat(data['request_date']) if data.get('request_date') else None
        )

        if updated_request is None:
            return jsonify({'error': 'DS_Request not found'}), 404

        return jsonify({
            'id': updated_request.id,
            'DistributionCenterID': updated_request.DistributionCenterID,
            'amount_of_meals': updated_request.amount_of_meals,
            'request_date': updated_request.request_date.isoformat()
        })
    finally:
        db_session.close()


# מחיקת בקשה (DELETE)
@ds_request_bp.route('/<int:request_id>', methods=['DELETE'])
def delete_request(request_id):
    db_session = SessionLocal()
    try:
        repo = DSRequestRepository(db_session)
        success = repo.delete_request(request_id)
        if not success:
            return jsonify({'error': 'DS_Request not found'}), 404
        return jsonify({'message': 'DS_Request deleted successfully'})
    finally:
        db_session.close()