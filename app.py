from flask import Flask
from signalwire_swaig.core import SWAIG, SWAIGArgument
from dotenv import load_dotenv
import os
import logging
import random

load_dotenv()

logging.getLogger('werkzeug').setLevel(logging.WARNING)

if os.environ.get('DEBUG'):
    print("Debug mode is enabled")
    debug_pin = f"{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(100, 999)}"
    os.environ['WERKZEUG_DEBUG_PIN'] = debug_pin
    logging.getLogger('werkzeug').setLevel(logging.DEBUG)
    print(f"Debugger PIN: {debug_pin}")

app = Flask(__name__)
swaig = SWAIG(
    app,
    auth=(os.getenv('HTTP_USERNAME'), os.getenv('HTTP_PASSWORD'))
)

# Mock storage for appointments
appointments = {}

@swaig.endpoint("Manage appointment actions for HVAC, plumbing, or electrical needs",
                action=SWAIGArgument("string", "Type of action to perform", enum=["schedule", "update", "escalate", "search", "cancel"], required=True),
                service_type=SWAIGArgument("string", "Type of service required", enum=["HVAC", "plumbing", "electrical"]),
                name=SWAIGArgument("string", "Customer's full name"),
                contact_number=SWAIGArgument("string", "Customer's phone number", required=True),
                date=SWAIGArgument("string", "Preferred appointment date"),
                time=SWAIGArgument("string", "Preferred appointment time"),
                address=SWAIGArgument("string", "Street address for the service"),
                city=SWAIGArgument("string", "City for the service address"),
                state=SWAIGArgument("string", "State for the service address", enum=["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
                                                                                    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
                                                                                    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
                                                                                    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
                                                                                    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]),
                zip=SWAIGArgument("string", "5-digit ZIP code for the service address"),
                emergency_description=SWAIGArgument("string", "Detailed description of the emergency situation"))
def manage_appointment(action, service_type=None, name=None, contact_number=None, date=None, time=None, address=None, city=None, state=None, zip=None, emergency_description=None, meta_data_token=None, meta_data=None):
    if action == "schedule":
        appointments[contact_number] = {
            "service_type": service_type,
            "name": name,
            "date": date,
            "time": time,
            "address": address,
            "city": city,
            "state": state,
            "zip": zip
        }
        return f"Appointment scheduled for {service_type} service on {date} at {time}."
    
    elif action == "update":
        if contact_number in appointments:
            appointments[contact_number].update({
                "service_type": service_type or appointments[contact_number]["service_type"],
                "date": date or appointments[contact_number]["date"],
                "time": time or appointments[contact_number]["time"],
                "address": address or appointments[contact_number]["address"],
                "city": city or appointments[contact_number]["city"],
                "state": state or appointments[contact_number]["state"],
                "zip": zip or appointments[contact_number]["zip"]
            })
            return f"Appointment for {contact_number} updated."
        else:
            return "Appointment not found."
    
    elif action == "escalate":
        return f"Emergency escalated for {service_type} at {address}, {city}, {state} {zip}: {emergency_description}"
    
    elif action == "search":
        appointment = appointments.get(contact_number)
        if appointment:
            return f"Appointment for {appointment['service_type']} on {appointment['date']} at {appointment['time']} for {appointment['name']} at {appointment['address']}, {appointment['city']}, {appointment['state']} {appointment['zip']}."
        return "Appointment not found.", {"status": "error"}

    elif action == "cancel":
        if contact_number in appointments:
            del appointments[contact_number]
            return f"Appointment for {contact_number} canceled."
        else:
            return "Appointment not found."
    
    else:
        return "Invalid action specified."

@app.route('/', methods=['GET'])
@app.route('/swaig', methods=['GET'])
def display_appointments():
    return render_template('appointments.html', appointments=appointments)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True) 