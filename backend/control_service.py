from datetime import datetime

# Global state tracking for the system
command_history = []  # List of dictionaries to store all action logs
pump_state = "STOPPED"  # Initial state of the pump
valve_state = "CLOSED"  # Initial state of the valve


def log_command(device, command, status):
    """
    Creates a standardized log entry and appends it to the global history.
    Returns the created entry dictionary.
    """
    entry = {
        "device": device,
        "command": command,
        "status": status,
        "timestamp": datetime.now().isoformat()
    }

    command_history.append(entry)
    return entry


def control_pump(command):
    """
    Handles the logic for starting and stopping the pump.
    Prevents redundant commands (e.g., starting an already running pump).
    """
    global pump_state

    # Validation: Prevent the pump from being set to its current state
    if command == "START" and pump_state == "RUNNING":
        return log_command("pump", command, "FAILED")

    if command == "STOP" and pump_state == "STOPPED":
        return log_command("pump", command, "FAILED")

    # Update state based on valid input
    if command == "START":
        pump_state = "RUNNING"
    elif command == "STOP":
        pump_state = "STOPPED"

    return log_command("pump", command, "SUCCESS")


def control_valve(command):
    """
    Handles the logic for opening and closing the valve.
    Ensures the valve cannot be 'opened' if it is already open.
    """
    global valve_state

    # Validation: Ensure command changes the current state
    if command == "OPEN" and valve_state == "OPEN":
        return log_command("valve", command, "FAILED")

    if command == "CLOSE" and valve_state == "CLOSED":
        return log_command("valve", command, "FAILED")

    # Update state based on valid input
    if command == "OPEN":
        valve_state = "OPEN"
    elif command == "CLOSE":
        valve_state = "CLOSED"

    return log_command("valve", command, "SUCCESS")


def get_history():
    """
    Retrieves the complete list of logged actions for the system.
    """
    return command_history