# Import FastAPI framework to create the web server and API endpoints
from fastapi import FastAPI

# Import BaseModel from Pydantic to define and validate the data structure
from pydantic import BaseModel


# Create an instance of FastAPI
# This object is the main entry point of the application
app = FastAPI()


# Define the data model (Data Contract) for incoming sensor data
# This ensures the incoming JSON has the correct structure and types
class SensorData(BaseModel):
    device_id: str      # Unique identifier of the sensor device
    timestamp: str      # Time when the data was recorded
    water_level: float  # Current water level measured by the sensor
    flow_rate: float    # Current water flow rate measured by the sensor


# Health check endpoint
# This endpoint is used to verify that the server is running correctly
# It can be accessed via GET request at /health
@app.get("/health")
def health_check():
    # Return a simple status message
    return {"status": "Server running"}


# Data ingestion endpoint
# This endpoint receives sensor data via POST request at /ingest
# FastAPI automatically validates the incoming JSON using SensorData model
@app.post("/ingest")
def ingest(data: SensorData):
    
    # Print the received data to the console (for debugging and monitoring)
    print(data)

    # Return a confirmation response to the sender
    return {"message": "Data received"}
