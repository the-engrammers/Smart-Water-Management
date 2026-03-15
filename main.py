import sys
import os
from fastapi import FastAPI

# Add the backend folder to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

# Import the app instance from your renamed file
from app_logic import app 

# This makes sure Uvicorn finds the 'app' variable correctly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)