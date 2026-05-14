from flask import Blueprint, request, jsonify
from repository.recipient_request_repository import RecipientRequestRepository
from db_connection import SessionLocal
from datetime import datetime

# Blueprint עבור Recipient_Request
recipient_request_bp = Blueprint('recipient_request_bp', __name__, url_prefix='/recipient_request')

# יצירת בקשה חדשה (POST)
@recipient_request_bp.route('', methods=['POST'])
def add_recipient_request():
    db_session = SessionLocal()
    try:
        repo = RecipientRequestRepository(db_session)
        data = request.get_json()

        new_request = repo.create_request(
            recipient_id=data['RecipientID'],
            amount_of_meals=data['amount_of_meals'],
            request_date=datetime.fromisoformat(data['request_date']) if data.get('request_date') else None
        )

        return jsonify({
            'id': new_request.id,
            'RecipientID': new_request.RecipientID,
            'amount_of_meals': new_request.amount_of_meals,
            'request_date': new_request.request_date.isoformat()
        }), 201

    finally:
        db_session.close()


# קבלת בקשה לפי ID (GET)
@recipient_request_bp.route('/<int:request_id>', methods=['GET'])
def get_recipient_request(request_id):
    db_session = SessionLocal()
    try:
        repo = RecipientRequestRepository(db_session)
        request_obj = repo.get_request(request_id)
        if request_obj is None:
            return jsonify({'error': 'Recipient_Request not found'}), 404

        return jsonify({
            'id': request_obj.id,
            'RecipientID': request_obj.RecipientID,
            'amount_of_meals': request_obj.amount_of_meals,
            'request_date': request_obj.request_date.isoformat()
        })
    finally:
        db_session.close()


# עדכון בקשה (PUT)
@recipient_request_bp.route('/<int:request_id>', methods=['PUT'])
def update_recipient_request(request_id):
    db_session = SessionLocal()
    try:
        repo = RecipientRequestRepository(db_session)
        data = request.get_json()

        updated_request = repo.update_request(
            request_id,
            amount_of_meals=data.get('amount_of_meals'),
            request_date=datetime.fromisoformat(data['request_date']) if data.get('request_date') else None
        )

        if updated_request is None:
            return jsonify({'error': 'Recipient_Request not found'}), 404

        return jsonify({
            'id': updated_request.id,
            'RecipientID': updated_request.RecipientID,
            'amount_of_meals': updated_request.amount_of_meals,
            'request_date': updated_request.request_date.isoformat()
        })
    finally:
        db_session.close()


# מחיקת בקשה (DELETE)
@recipient_request_bp.route('/<int:request_id>', methods=['DELETE'])
def delete_recipient_request(request_id):
    db_session = SessionLocal()
    try:
        repo = RecipientRequestRepository(db_session)
        success = repo.delete_request(request_id)
        if not success:
            return jsonify({'error': 'Recipient_Request not found'}), 404
        return jsonify({'message': 'Recipient_Request deleted successfully'})
    finally:
        db_session.close()