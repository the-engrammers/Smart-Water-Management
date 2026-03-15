import pandas as pd
from sqlalchemy import create_engine
import os

# 1. Get the directory where THIS script is located
base_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Define absolute paths
# This goes up one level from 'database' then into 'data'
csv_path = os.path.join(base_dir, "..", "data", "Aquifer_Petrignano.csv")
db_path = f"sqlite:///{os.path.join(base_dir, '..', 'water_management.db')}"

# 3. Connection
engine = create_engine(db_path)

def migrate():
    print(f"Checking for file at: {csv_path}")
    
    if not os.path.exists(csv_path):
        print(f" Error: CSV still not found. Check if the file is in: {csv_path}")
        return

    # 4. Read and Clean
    print("Reading CSV...")
    df = pd.read_csv(csv_path)
    
    # 5. Load into SQL
    try:
        # if_exists='replace' creates the table if it doesn't exist
        df.to_sql('sensor_data', con=engine, if_exists='replace', index=False)
        print(" Success! Data migrated to water_management.db")
    except Exception as e:
        print(f" Migration failed: {e}")

if __name__ == "__main__":
    migrate()