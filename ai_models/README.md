# AI Models

## Leak Detection
- Script: `ai_models/leak_detection.py`
- Data source: `data/Aquifer_Petrignano.csv`
- Outputs:
	- `ai_models/leak_detection_model.pkl`
	- `ai_models/leak_scaler.pkl`

Run:
```bash
python ai_models/leak_detection.py
```

## Demand Forecasting
- Script: `ai_models/demand_forecasting/train_model.py`
- Expects cleaned data with: `timestamp`, `flow_rate`, `temperature`

Run from Python:
```python
from ai_models.demand_forecasting.train_model import train_model
train_model("path/to/cleaned_data.csv")
```

