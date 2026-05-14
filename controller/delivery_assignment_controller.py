from flask import Blueprint, request, jsonify
from repository.delivery_assignmentRepository import DeliveryAssignmentRepository
from db_connection import SessionLocal

# Blueprint עבור DeliveryAssignment
delivery_assignment_bp = Blueprint('delivery_assignment_bp', __name__, url_prefix='/delivery_assignment')

# יצירת משלוח חדש (POST)
@delivery_assignment_bp.route('', methods=['POST'])
def add_delivery_assignment():
    db_session = SessionLocal()
    try:
        repo = DeliveryAssignmentRepository(db_session)
        data = request.get_json()

        new_assignment = repo.create_delivery_assignment(
            DistributionCenterID=data['DistributionCenterID'],
            RecipientID=data['RecipientID'],
            VolunteerID=data['VolunteerID'],
            amount_of_meals=data['amount_of_meals']
        )

        return jsonify({
            'id': new_assignment.id,
            'DistributionCenterID': new_assignment.DistributionCenterID,
            'RecipientID': new_assignment.RecipientID,
            'VolunteerID': new_assignment.VolunteerID,
            'amount_of_meals': new_assignment.amount_of_meals
        }), 201

    finally:
        db_session.close()


# קבלת משלוח לפי ID (GET)
@delivery_assignment_bp.route('/<int:assignment_id>', methods=['GET'])
def get_delivery_assignment(assignment_id):
    db_session = SessionLocal()
    try:
        repo = DeliveryAssignmentRepository(db_session)
        assignment = repo.get_delivery_assignment(assignment_id)
        if not assignment:
            return jsonify({'error': 'DeliveryAssignment not found'}), 404

        return jsonify({
            'id': assignment.id,
            'DistributionCenterID': assignment.DistributionCenterID,
            'RecipientID': assignment.RecipientID,
            'VolunteerID': assignment.VolunteerID,
            'amount_of_meals': assignment.amount_of_meals
        })
    finally:
        db_session.close()


# עדכון משלוח (PUT)
@delivery_assignment_bp.route('/<int:assignment_id>', methods=['PUT'])
def update_delivery_assignment(assignment_id):
    db_session = SessionLocal()
    try:
        repo = DeliveryAssignmentRepository(db_session)
        data = request.get_json()

        updated_assignment = repo.update_delivery_assignment(
            assignmentID=assignment_id,
            DistributionCenterID=data.get('DistributionCenterID'),
            RecipientID=data.get('RecipientID'),
            VolunteerID=data.get('VolunteerID'),
            amount_of_meals=data.get('amount_of_meals')
        )

        if not updated_assignment:
            return jsonify({'error': 'DeliveryAssignment not found'}), 404

        return jsonify({
            'id': updated_assignment.id,
            'DistributionCenterID': updated_assignment.DistributionCenterID,
            'RecipientID': updated_assignment.RecipientID,
            'VolunteerID': updated_assignment.VolunteerID,
            'amount_of_meals': updated_assignment.amount_of_meals
        })
    finally:
        db_session.close()


# מחיקת משלוח (DELETE)
@delivery_assignment_bp.route('/<int:assignment_id>', methods=['DELETE'])
def delete_delivery_assignment(assignment_id):
    db_session = SessionLocal()
    try:
        repo = DeliveryAssignmentRepository(db_session)
        success = repo.delete_delivery_assignment(assignment_id)
        if not success:
            return jsonify({'error': 'DeliveryAssignment not found'}), 404
        return jsonify({'message': 'DeliveryAssignment deleted successfully'})
    finally:
        db_session.close()