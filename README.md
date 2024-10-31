Here’s the updated document with `cancel` and `search` incorporated as actions within the `manage_appointment` tool. This allows all appointment management tasks to be handled by a single tool.

---

# Wendy - After-Hours Answering Service AI Agent for HVAC/Plumbing/Electrical

## Table of Contents

1. [Introduction](#introduction)
2. [System Overview](#system-overview)
3. [Expanded Requirements](#expanded-requirements)
4. [SWML / SWAIG Tool](#swml--swaig-tool)
   - [Tool: `manage_appointment`](#tool-manage_appointment)
5. [Mock Data Structure](#mock-data-structure)
6. [Python Code Structure with Mock Functions](#python-code-structure-with-mock-functions)
7. [System Prompt](#system-prompt)
8. [Post-Conversation Summarization Prompt](#post-conversation-summarization-prompt)

---

## 1. Introduction

Wendy is an AI Agent providing after-hours answering services for an HVAC, Plumbing, and Electrical business. Wendy can handle scheduling, updating, escalating, searching, and canceling appointments, collect system-specific information, and provide general business details. Each operation is managed through a unified `manage_appointment` tool with an `action` parameter specifying the task.

---

## 2. System Overview

The `manage_appointment` tool consolidates all appointment management actions, including scheduling, updating, escalating, searching, and canceling appointments. Wendy uses the customer’s phone number in E.164 format as the unique identifier for each appointment.

---

## 3. Expanded Requirements

- **Single Tool with Multiple Actions**: Appointment management actions (schedule, update, escalate, search, cancel) are combined into a single tool with an `action` parameter.
- **Complete Address Information**: Wendy collects the full address, including city, state, and `zip`.

---

## 4. SWML / SWAIG Tool

### Tool: `manage_appointment`

- **Description**: Manages various appointment actions, such as scheduling, updating, escalating, searching, and canceling an appointment.
- **Tool Name**: `manage_appointment`
- **Parameters**:

  ```json
  {
    "function": "manage_appointment",
    "description": "Manage appointment actions for HVAC, plumbing, or electrical needs, including scheduling, updating, escalating emergencies, searching, and canceling.",
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
          "type": "string",
          "pattern": "^[0-9]{5}$"
        },
        "emergency_description": {
          "description": "Detailed description of the emergency situation. Required for 'escalate' action.",
          "type": "string"
        }
      },
      "required": ["action", "contact_number"]
    }
  }
  ```

---

## 5. Mock Data Structure

The AI Agent uses in-memory data storage with the customer’s phone number in E.164 format as the unique identifier for each appointment.

---

## 6. Python Code Structure with Mock Functions

Here’s the Python code implementing the `manage_appointment` tool with all required actions.

```python
# Mock storage for appointments
appointments = {}

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
```

---

## 7. System Prompt

**System Prompt for After-Hours AI Agent "Wendy"**:

"You are Wendy, the AI assistant for an HVAC, Plumbing, and Electrical business’s after-hours answering service. Guide customers through scheduling appointments, collecting information about their system, escalating emergencies, searching for appointments, and answering general inquiries.

1. **Introduce Yourself**: *“Hi, this is Wendy, your after-hours assistant from [Business Name]. How can I help?”*
2. **Step-by-Step Information Gathering**: Ask for one piece of information at a time.
3. **Verify Contact**: Use the phone number on file as the unique identifier for appointments.
4. **Handle Emergencies**: If an emergency is reported, escalate it to on-call staff.
5. **Collect HVAC System Details**: Gather HVAC system type, warranty status, and prior service history when relevant.

Guide the user smoothly, confirm information accurately

, and prepare all details for technician follow-up."

---

## 8. Post-Conversation Summarization Prompt

**Summarization Prompt**:

"Summarize this conversation, noting the customer’s service request type (HVAC, plumbing, electrical), appointment or emergency details, system information (e.g., warranty status, prior service), and confirm the preferred contact method. Provide a clear summary for technicians, including all relevant customer details."
