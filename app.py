from flask import Flask, request, jsonify, render_template
from flask_httpauth import HTTPBasicAuth
from dotenv import load_dotenv

import os

load_dotenv()

app = Flask(__name__)
auth = HTTPBasicAuth()

# Mock storage for appointments
appointments = {}

# Load environment variables
HTTP_USERNAME = os.getenv('HTTP_USERNAME')
HTTP_PASSWORD = os.getenv('HTTP_PASSWORD')

@auth.verify_password
def verify_password(username, password):
    return username == HTTP_USERNAME and password == HTTP_PASSWORD

SWAIG_FUNCTION_SIGNATURES = {
    "manage_appointment": {
        "description": "Manage appointment actions for HVAC, plumbing, or electrical needs, including scheduling, updating, escalating emergencies, searching, and canceling.",
        "function": "manage_appointment",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "description": "Type of action to perform. Must be one of: 'schedule', 'update', 'escalate', 'search', or 'cancel'.",
                    "type": "string",
                    "enum": ["schedule", "update", "escalate", "search", "cancel"]
                },
                "service_type": {
                    "description": "Type of service required for 'schedule' or 'escalate' actions. Must be one of: 'HVAC', 'plumbing', or 'electrical'.",
                    "type": "string",
                    "enum": ["HVAC", "plumbing", "electrical"]
                },
                "name": {
                    "description": "Customer's full name for the appointment (e.g., 'John Doe'). Required for 'schedule' and 'escalate' actions.",
                    "type": "string"
                },
                "contact_number": {
                    "description": "Customer's phone number in E.164 format (e.g., '+1234567890'). Used as the unique identifier for appointments.",
                    "type": "string"
                },
                "date": {
                    "description": "Preferred appointment date in 'YYYY-MM-DD' format. Required for 'schedule' and 'update' actions.",
                    "type": "string"
                },
                "time": {
                    "description": "Preferred appointment time in 'HH:MM' 24-hour format. Required for 'schedule' and 'update' actions.",
                    "type": "string"
                },
                "address": {
                    "description": "Street address for the service. Required for 'schedule' and 'escalate' actions.",
                    "type": "string"
                },
                "city": {
                    "description": "City for the service address. Required for 'schedule' and 'escalate' actions.",
                    "type": "string"
                },
                "state": {
                    "description": "State for the service address as a two-letter abbreviation. Must be one of the 50 U.S. states. Required for 'schedule' and 'escalate' actions.",
                    "type": "string",
                    "enum": ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
                             "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
                             "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
                             "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
                             "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
                },
                "zip": {
                    "description": "5-digit ZIP code for the service address (e.g., '10001'). Required for 'schedule' and 'escalate' actions.",
                    "type": "string"
                },
                "emergency_description": {
                    "description": "Detailed description of the emergency situation. Required for 'escalate' action.",
                    "type": "string"
                }
            },
            "required": ["action", "contact_number"]
        }
    }
}

@app.route('/swaig', methods=['POST'])
@auth.login_required
def swaig():
    data = request.json
    action = data.get('action')

    if action == "get_signature":
        requested_functions = data.get("functions", [])
        if not requested_functions:
            requested_functions = list(SWAIG_FUNCTION_SIGNATURES.keys())

        response = [
            SWAIG_FUNCTION_SIGNATURES[func]
            for func in requested_functions
            if func in SWAIG_FUNCTION_SIGNATURES
        ]

        missing_functions = [
            func for func in requested_functions
            if func not in SWAIG_FUNCTION_SIGNATURES
        ]

        if missing_functions:
            print(f"Missing functions: {missing_functions}")

        return jsonify(response)

    else:
        function_name = data.get('function')
        params = data.get('parameters', {})
        print(f"Function name: {function_name}, Params: {params}")

        if function_name == "manage_appointment":
            response = manage_appointment(params)
            return jsonify(response)
        else:
            return jsonify({"error": "Function not found"}), 404

def manage_appointment(data):
    action = data["action"]
    contact_number = data["contact_number"]
    
    if action == "schedule":
        appointments[contact_number] = {
            "service_type": data["service_type"],
            "name": data["name"],
            "date": data["date"],
            "time": data["time"],
            "address": data["address"],
            "city": data["city"],
            "state": data["state"],
            "zip": data["zip"]
        }
        return {"response": f"Appointment scheduled for {data['service_type']} service on {data['date']} at {data['time']}."}
    
    elif action == "update":
        if contact_number in appointments:
            appointments[contact_number].update({
                "service_type": data.get("service_type", appointments[contact_number]["service_type"]),
                "date": data.get("date", appointments[contact_number]["date"]),
                "time": data.get("time", appointments[contact_number]["time"]),
                "address": data.get("address", appointments[contact_number]["address"]),
                "city": data.get("city", appointments[contact_number]["city"]),
                "state": data.get("state", appointments[contact_number]["state"]),
                "zip": data.get("zip", appointments[contact_number]["zip"])
            })
            return {"response": f"Appointment for {contact_number} updated."}
        else:
            return {"response": "Appointment not found."}
    
    elif action == "escalate":
        return {"response": f"Emergency escalated for {data['service_type']} at {data['address']}, {data['city']}, {data['state']} {data['zip']}: {data['emergency_description']}"}
    
    elif action == "search":
        appointment = appointments.get(contact_number)
        if appointment:
            return {"response": f"Appointment for {appointment['service_type']} on {appointment['date']} at {appointment['time']} for {appointment['name']} at {appointment['address']}, {appointment['city']}, {appointment['state']} {appointment['zip']}."}
        return {"response": "Appointment not found."}

    elif action == "cancel":
        if contact_number in appointments:
            del appointments[contact_number]
            return {"response": f"Appointment for {contact_number} canceled."}
        else:
            return {"response": "Appointment not found."}
    
    else:
        return {"response": "Invalid action specified."}

@app.route('/', methods=['GET'])
@app.route('/swaig', methods=['GET'])
def display_appointments():
    return render_template('appointments.html', appointments=appointments)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True) 