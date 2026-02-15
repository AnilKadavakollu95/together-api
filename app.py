from flask import Flask, request, jsonify
import random
import string
from datetime import datetime

app = Flask(__name__)

# Store OTPs temporarily (in-memory)
otp_store = {}

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "Welcome to Together API",
        "version": "1.0",
        "endpoints": {
            "request_otp": "/api/auth/request-otp/",
            "verify_otp": "/api/auth/verify-otp/"
        }
    })

@app.route('/api/auth/request-otp/', methods=['POST'])
def request_otp():
    data = request.get_json()
    phone = data.get('phone')
    email = data.get('email')
    
    if not phone and not email:
        return jsonify({"error": "Phone or Email is required"}), 400
    
    # Generate random 6-digit OTP
    otp = ''.join(random.choices(string.digits, k=6))
    
    identifier = phone or email
    otp_store[identifier] = {
        "otp": otp,
        "created_at": datetime.now(),
        "verified": False
    }
    
    return jsonify({
        "success": True,
        "message": "OTP sent successfully",
        "identifier": identifier,
        "otp": otp  # In production, send via SMS/Email
    }), 200

@app.route('/api/auth/verify-otp/', methods=['POST'])
def verify_otp():
    data = request.get_json()
    phone = data.get('phone')
    email = data.get('email')
    otp = data.get('otp')
    
    if not otp:
        return jsonify({"error": "OTP is required"}), 400
    
    identifier = phone or email
    
    if identifier not in otp_store:
        return jsonify({"error": "No OTP request found"}), 400
    
    if otp_store[identifier]["otp"] == otp:
        otp_store[identifier]["verified"] = True
        return jsonify({
            "success": True,
            "message": "OTP verified successfully",
            "token": f"token_{identifier}_{datetime.now().timestamp()}"
        }), 200
    else:
        return jsonify({"error": "Invalid OTP"}), 401

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
