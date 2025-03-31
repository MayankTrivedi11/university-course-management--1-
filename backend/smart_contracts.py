from flask import Blueprint, request, jsonify
from models import db, Course, User, Enrollment
from auth import jwt_required, get_jwt_identity
import os
import json
import base64
import algosdk
from algosdk.v2client import algod
from algosdk.future import transaction
from algosdk.future.transaction import PaymentTxn, AssetConfigTxn, AssetTransferTxn, AssetOptInTxn
from algosdk.v2client import indexer
import logging

smart_contracts_bp = Blueprint('smart_contracts', __name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Algorand client configuration
def get_algod_client():
    algod_address = os.environ.get("ALGORAND_ALGOD_ADDRESS", "https://testnet-api.algonode.cloud")
    algod_token = os.environ.get("ALGORAND_API_KEY", "")
    
    try:
        algod_client = algod.AlgodClient(algod_token, algod_address)
        return algod_client
    except Exception as e:
        logger.error(f"Error creating Algorand client: {str(e)}")
        return None

def get_indexer_client():
    indexer_address = os.environ.get("ALGORAND_INDEXER_ADDRESS", "https://testnet-idx.algonode.cloud")
    indexer_token = os.environ.get("ALGORAND_API_KEY", "")
    
    try:
        indexer_client = indexer.IndexerClient(indexer_token, indexer_address)
        return indexer_client
    except Exception as e:
        logger.error(f"Error creating Indexer client: {str(e)}")
        return None

# Function to create a new course smart contract on Algorand
def create_course_contract(course):
    try:
        # Get admin account
        admin_private_key = os.environ.get("ALGORAND_ADMIN_PRIVATE_KEY")
        if not admin_private_key:
            logger.error("Admin private key not found in environment variables")
            return None
        
        private_key = base64.b64decode(admin_private_key)
        admin_account = algosdk.account.address_from_private_key(private_key)
        
        # Get Algorand client
        algod_client = get_algod_client()
        if not algod_client:
            return None
        
        # Get suggested parameters for transaction
        params = algod_client.suggested_params()
        
        # Create a new asset for the course
        # The asset will represent enrollment rights in the course
        txn = AssetConfigTxn(
            sender=admin_account,
            sp=params,
            total=course.capacity,
            default_frozen=False,
            unit_name=f"C{course.id}",
            asset_name=f"Course_{course.code}",
            manager=admin_account,
            reserve=admin_account,
            freeze=admin_account,
            clawback=admin_account,
            url=f"https://university.edu/courses/{course.id}",
            decimals=0,
            note=json.dumps({
                "course_id": course.id,
                "title": course.title,
                "code": course.code,
                "credits": course.credits,
                "capacity": course.capacity,
                "fee": course.fee
            }).encode()
        )
        
        # Sign transaction
        signed_txn = txn.sign(private_key)
        
        # Send transaction
        txid = algod_client.send_transaction(signed_txn)
        logger.info(f"Asset creation transaction ID: {txid}")
        
        # Wait for confirmation
        try:
            confirmed_txn = transaction.wait_for_confirmation(algod_client, txid, 4)
            logger.info(f"Transaction confirmed in round: {confirmed_txn['confirmed-round']}")
            
            # Get asset ID
            asset_id = confirmed_txn["asset-index"]
            logger.info(f"Asset ID: {asset_id}")
            
            # Return asset ID as contract address
            return str(asset_id)
        
        except Exception as e:
            logger.error(f"Error waiting for confirmation: {str(e)}")
            return None
    
    except Exception as e:
        logger.error(f"Error creating course contract: {str(e)}")
        return None

# Function to enroll a student in a course using Algorand
def enroll_student(contract_address, student_id, course_id):
    try:
        # Get admin account
        admin_private_key = os.environ.get("ALGORAND_ADMIN_PRIVATE_KEY")
        if not admin_private_key:
            logger.error("Admin private key not found in environment variables")
            return None
        
        private_key = base64.b64decode(admin_private_key)
        admin_account = algosdk.account.address_from_private_key(private_key)
        
        # Get Algorand client
        algod_client = get_algod_client()
        if not algod_client:
            return None
        
        # Get suggested parameters for transaction
        params = algod_client.suggested_params()
        
        # Create opt-in transaction for the student
        # In a real system, the student would have their own Algorand account
        # For demo purposes, we're using the admin account to represent the student
        asset_id = int(contract_address)
        
        # Record the enrollment by sending a 0 quantity of the asset to the admin (representing the student)
        txn = AssetTransferTxn(
            sender=admin_account,
            sp=params,
            receiver=admin_account,
            amt=1,
            index=asset_id,
            note=json.dumps({
                "action": "enroll",
                "student_id": student_id,
                "course_id": course_id,
                "timestamp": str(int(datetime.datetime.now().timestamp()))
            }).encode()
        )
        
        # Sign transaction
        signed_txn = txn.sign(private_key)
        
        # Send transaction
        txid = algod_client.send_transaction(signed_txn)
        logger.info(f"Enrollment transaction ID: {txid}")
        
        # Wait for confirmation
        try:
            confirmed_txn = transaction.wait_for_confirmation(algod_client, txid, 4)
            logger.info(f"Transaction confirmed in round: {confirmed_txn['confirmed-round']}")
            
            # Return transaction ID
            return txid
        
        except Exception as e:
            logger.error(f"Error waiting for confirmation: {str(e)}")
            return None
    
    except Exception as e:
        logger.error(f"Error enrolling student: {str(e)}")
        return None

@smart_contracts_bp.route('/verify-enrollment/<int:enrollment_id>', methods=['GET'])
@jwt_required
def verify_enrollment(enrollment_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    enrollment = Enrollment.query.get(enrollment_id)
    if not enrollment:
        return jsonify({"error": "Enrollment not found"}), 404
    
    # Check permissions
    if user.role == 'student' and enrollment.student_id != user.id:
        return jsonify({"error": "Permission denied"}), 403
    
    course = Course.query.get(enrollment.course_id)
    if not course or not course.contract_address:
        return jsonify({"error": "Course has no blockchain contract"}), 400
    
    # If there's no transaction ID, it wasn't recorded on blockchain
    if not enrollment.transaction_id:
        return jsonify({
            "verified": False,
            "message": "Enrollment not verified on blockchain"
        })
    
    # Verify on blockchain
    try:
        indexer_client = get_indexer_client()
        if not indexer_client:
            return jsonify({"error": "Unable to connect to blockchain"}), 500
        
        # Look up transaction
        transaction_info = indexer_client.transaction(enrollment.transaction_id)
        
        # Verify transaction exists and is valid
        if 'transaction' in transaction_info:
            txn = transaction_info['transaction']
            
            # Verify this is for the right asset/course
            if 'asset-transfer-transaction' in txn and txn['asset-transfer-transaction']['asset-id'] == int(course.contract_address):
                
                # If we have a note with enrollment data, parse and verify it
                if 'note' in txn:
                    try:
                        note_bytes = base64.b64decode(txn['note'])
                        note_json = json.loads(note_bytes)
                        
                        if (note_json.get('action') == 'enroll' and 
                            int(note_json.get('student_id')) == enrollment.student_id and
                            int(note_json.get('course_id')) == enrollment.course_id):
                            
                            return jsonify({
                                "verified": True,
                                "blockchain_data": {
                                    "transaction_id": enrollment.transaction_id,
                                    "confirmed_round": txn.get('confirmed-round'),
                                    "timestamp": note_json.get('timestamp'),
                                    "fee": txn.get('fee')
                                }
                            })
                    
                    except Exception as e:
                        logger.error(f"Error parsing transaction note: {str(e)}")
        
        # If we get here, verification failed
        return jsonify({
            "verified": False,
            "message": "Unable to verify enrollment on blockchain",
            "transaction_id": enrollment.transaction_id
        })
    
    except Exception as e:
        logger.error(f"Error verifying enrollment: {str(e)}")
        return jsonify({"error": str(e)}), 500

@smart_contracts_bp.route('/course/<int:course_id>/certificate', methods=['POST'])
@jwt_required
def generate_certificate(course_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": "Course not found"}), 404
    
    # Check if user is enrolled and has passed the course
    enrollment = Enrollment.query.filter_by(
        student_id=current_user_id,
        course_id=course_id
    ).first()
    
    if not enrollment:
        return jsonify({"error": "Not enrolled in this course"}), 403
    
    if not enrollment.grade or enrollment.grade in ['F', 'Incomplete']:
        return jsonify({"error": "Course not completed with passing grade"}), 400
    
    try:
        # Get admin account
        admin_private_key = os.environ.get("ALGORAND_ADMIN_PRIVATE_KEY")
        if not admin_private_key:
            logger.error("Admin private key not found in environment variables")
            return jsonify({"error": "Blockchain configuration error"}), 500
        
        private_key = base64.b64decode(admin_private_key)
        admin_account = algosdk.account.address_from_private_key(private_key)
        
        # Get Algorand client
        algod_client = get_algod_client()
        if not algod_client:
            return jsonify({"error": "Unable to connect to blockchain"}), 500
        
        # Get suggested parameters for transaction
        params = algod_client.suggested_params()
        
        # Create a certificate as a new asset
        txn = AssetConfigTxn(
            sender=admin_account,
            sp=params,
            total=1,  # Only one certificate per student per course
            default_frozen=False,
            unit_name="CERT",
            asset_name=f"Certificate_{course.code}_{user.id}",
            manager=admin_account,
            reserve=admin_account,
            freeze=admin_account,
            clawback=admin_account,
            url=f"https://university.edu/certificates/{course.id}/{user.id}",
            decimals=0,
            note=json.dumps({
                "type": "course_certificate",
                "student_id": user.id,
                "student_name": user.name,
                "course_id": course.id,
                "course_code": course.code,
                "course_title": course.title,
                "grade": enrollment.grade,
                "credits": course.credits,
                "date_issued": datetime.datetime.utcnow().isoformat()
            }).encode()
        )
        
        # Sign transaction
        signed_txn = txn.sign(private_key)
        
        # Send transaction
        txid = algod_client.send_transaction(signed_txn)
        logger.info(f"Certificate creation transaction ID: {txid}")
        
        # Wait for confirmation
        confirmed_txn = transaction.wait_for_confirmation(algod_client, txid, 4)
        logger.info(f"Transaction confirmed in round: {confirmed_txn['confirmed-round']}")
        
        # Get asset ID
        asset_id = confirmed_txn["asset-index"]
        logger.info(f"Certificate Asset ID: {asset_id}")
        
        return jsonify({
            "message": "Course certificate generated successfully",
            "certificate": {
                "asset_id": asset_id,
                "transaction_id": txid,
                "student_id": user.id,
                "student_name": user.name,
                "course_code": course.code,
                "course_title": course.title,
                "grade": enrollment.grade,
                "date_issued": datetime.datetime.utcnow().isoformat()
            }
        })
    
    except Exception as e:
        logger.error(f"Error generating certificate: {str(e)}")
        return jsonify({"error": str(e)}), 500

